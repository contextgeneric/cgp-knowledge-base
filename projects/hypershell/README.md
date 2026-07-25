# Hypershell

Hypershell is a modular, **type-level DSL** for writing shell-script-like programs in Rust: a program
is an ordinary Rust *type*, and the context that runs it is the interpreter, so both the language's
syntax and its semantics can be extended without touching the core library.

- **Repository** — <https://github.com/contextgeneric/hypershell>
- **Local checkout** — `../hypershell`, per [sibling-projects.md](../../sibling-projects.md)
- **Crate** — [`hypershell`](https://crates.io/crates/hypershell) 0.1.0
- **Tracks** — `cgp` 0.8.0-alpha
- **Status** — Experimental proof of concept, stated as such by the project itself

## What it is

A Hypershell program looks like a shell pipeline and is written with the `hypershell!` macro, whose
surface syntax — a `|` operator, bracketed variadic lists, bare string literals — desugars into plain
Rust types: `Pipe<Product![...]>` over `Symbol!` type-level strings. Running one means calling
`handle` on a context, which interprets the program at compile time into direct, statically dispatched
Rust.

The DSL covers CLI execution in both a simple form and a streaming form that spawns child processes
and pipes their standard streams; native HTTP requests, likewise simple and streaming; JSON encoding
and decoding; file reads and writes; WebSocket connections; and a set of adapters that convert between
the stream types those handlers produce and consume. Arguments may be static or read from a field on
the running context, which is how a program parameterizes over runtime values it cannot hold itself.

The project is explicit that it is a demonstration rather than a shell replacement. Its purpose is to
show that CGP can host a DSL whose users need not learn CGP.

## How it is organized

The crate layout is the point rather than an incidental detail, because it demonstrates the
dependency-graph inversion CGP produces: because implementations are written against abstract
contexts and concrete types are named last, each crate depends only on what it actually uses.

`hypershell-components` defines the abstract syntax — the empty `PhantomData` structs like
`SimpleExec` and `StreamingExec` that a program is written from — together with the component
interfaces they are interpreted through, and depends on nothing but `cgp`.
`hypershell-tokio-components` implements CLI execution on Tokio, `hypershell-reqwest-components`
implements HTTP on `reqwest`, and `hypershell-json-components`, `hypershell-hash-components`, and
`hypershell-tungstenite-components` add JSON, checksumming, and WebSockets respectively — each
depending on `cgp`, the components crate, and its own backend, and on none of the others.
`hypershell-macro` provides the surface syntax, `hypershell` assembles the concrete contexts, and
`hypershell-examples` holds runnable programs.

The assembly crate is small and worth reading first. It defines one namespace,
`HypershellNamespace`, inheriting `DefaultNamespace` and mapping path-prefixed keys such as
`@cgp.core.error.ErrorTypeProviderComponent` and `@hypershell.reqwest.ReqwestClientGetterComponent` to
providers drawn from the backend crates. A context then joins it in a single statement — `HypershellCli`
is an empty struct whose entire wiring is `namespace HypershellNamespace;`, and `HypershellHttp` adds
one `http_client` field. A user's own context does the same and gains the whole language.

## What CGP it exercises

Hypershell is the reference implementation of
[type-level DSLs](../../cgp/concepts/type-level-dsls.md), and the technique is documented end to end
in the [shell-scripting DSL example](../../examples/shell-scripting-dsl.md), which re-derives the
project's core in verified current syntax and is the source other documents quote.

Its central component is [`Handler` / `CanHandle`](../../cgp/reference/components/handler.md) from the
[handler family](../../cgp/concepts/handlers.md) — indeed the family was introduced in CGP v0.4.1
specifically to support this project. Each handler provider pattern-matches the `Code` parameter to
destructure a syntax type, which is [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) used as an
interpreter, and pulls what it needs from the context through
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md). Errors are handled through
[modular error handling](../../cgp/concepts/modular-error-handling.md), with
[`CanRaiseError` and `CanWrapError`](../../cgp/reference/components/can_raise_error.md) letting a
provider report an `std::io::Error` or a missing command without ever naming a concrete error type.
Pipelines compose with [`PipeHandlers`](../../cgp/reference/providers/handler_combinators.md), routing
uses [dispatching](../../cgp/concepts/dispatching.md), and the whole wiring is organized with
[namespaces](../../cgp/concepts/namespaces.md). The type-level vocabulary a program is written in is
[`Symbol!`](../../cgp/reference/macros/symbol.md) and
[`Product!`](../../cgp/reference/macros/product.md).

Two properties make it a good stress test rather than only a demo. Extending the language requires no
upstream coordination: a new syntax type, a provider for it, and a namespace that adds the entry are
enough, and the project's own `hypershell-hash-components` crate is exactly that. And swapping a
backend needs no feature flags, because alternative providers coexist rather than excluding one
another.

## How it relates to the rest of the base

The [announcement post](../../website/blog/hypershell-release.md) is the fullest published account of
the project and of the DSL technique, but it was written against CGP v0.4.1 and its wiring code is
three breaking releases stale — that document records exactly what. **Do not take current syntax from
it**; use the [example](../../examples/shell-scripting-dsl.md) or the project's own source.

The project also appears on the website's [Resources page](../../website/site-structure.md), and it is
one of the concrete artifacts the
[communication strategy](../../communication-strategy/attention-and-engagement.md) counts as social
proof for the evaluator profile.

## Status and gaps

The project tracks the current library — it depends on `cgp` 0.8.0-alpha and has been migrated from
the removed preset system to namespaces — so its source is a reliable reference for current CGP even
though its announcement post is not. Its published crate version is 0.1.0 and the README still shows
`cgp = "0.4.1"` in the install snippet, which is the most visible thing about it that has fallen
behind.

Its documentation is thin by design: the README is an overview and points at the blog post for
everything else, which means the only substantial prose about the project is the stale one. Writing
current material for Hypershell is therefore an open task, and this document is deliberately brief
pending that work.
