# Hypershell

Hypershell is a modular, type-level DSL for writing shell-script-like programs in Rust. A program is
an ordinary Rust type, and the context that runs it is the interpreter, so both the language's syntax
and its meaning can be extended without touching the core crates.

- **Repository** — <https://github.com/contextgeneric/hypershell>
- **Local checkout** — `../hypershell`, per [sibling-projects.md](../../sibling-projects.md)
- **Branch documented** — `v0.8.0`
- **Crates** — `hypershell`, `hypershell-components`, `hypershell-tokio-components`,
  `hypershell-reqwest-components`, `hypershell-json-components`, `hypershell-hash-components`,
  `hypershell-tungstenite-components`, `hypershell-macro`, all at 0.1.0, plus the unpublished
  `hypershell-examples`
- **Tracks** — `cgp` 0.8.0-alpha
- **Status** — Experimental proof of concept, stated as such by the project itself; see
  [Status and gaps](#status-and-gaps)

## What it is

A Hypershell program looks like a shell pipeline, written with the `hypershell!` macro, and is an
ordinary Rust type:

```rust
pub type Program = hypershell! {
        SimpleExec<
            StaticArg<"echo">,
            WithStaticArgs["hello", "world!"],
        >
    |   StreamToStdout
};
```

The macro only rewrites tokens: the `|` becomes a `Pipe<Product![…]>`, the bracket list a
`Product!`, and each string a `Symbol!`. Every piece of syntax is an empty marker struct, so nothing
in the program says how it runs. Running it is one call,
`context.handle(PhantomData::<Program>, input)`, and the compiler resolves each piece of syntax to
the provider the context's wiring chooses.
The program compiles to direct calls to those providers.

The language covers external commands, simple and streaming; HTTP requests with `reqwest`, simple and
streaming; file reads and writes; JSON encoding and decoding; and adapters between bytes and the
stream types those stages exchange. Two extension crates add native checksums and WebSockets.
Arguments may be literals or values read from fields of the running context, which is how a program
that is a type reads runtime values.

The project is explicit that it is a demonstration rather than a shell replacement. Its purpose is to
show that CGP can host a DSL whose users need not learn CGP, and that such a language can be extended
by anyone without upstream coordination.

## Which revision these documents describe

These documents describe the `v0.8.0` branch, which tracks `cgp` 0.8.0-alpha and is not yet
released. The repository's `main` branch tracks `cgp` 0.7.0, and the crates on crates.io are the
0.1.0 release (tag `v0.1.0`), built against `cgp` 0.4.1. All three carry version 0.1.0. They differ
in architecture, not only in syntax: the published release and `main` both assemble the language
from `cgp_preset!` presets, and `v0.8.0` is the only branch built on `HypershellNamespace`. It is
also the only one that dispatches on the input type with path keys, where `main` uses
`UseInputDelegate`. So code quoted from these documents compiles only against `v0.8.0`.
Source links point at that branch, per [../AGENTS.md](../AGENTS.md#a-project-section-documents-its-project-in-depth).

## How it is organized

The workspace holds eight library crates and an examples crate. The split follows backends, so a crate
compiles only the libraries it interprets. The layout is worked through in
[architecture/crate-layout.md](architecture/crate-layout.md).

- **`hypershell-components`** — the syntax types, the argument-extractor components, the control
  providers, and the base bundle. Depends only on `cgp`.
- **`hypershell-tokio-components`** — processes, files, streams, the stream wrapper types, and the
  input dispatchers, on Tokio.
- **`hypershell-reqwest-components`** — HTTP on `reqwest`.
- **`hypershell-json-components`** — JSON on `serde_json`.
- **`hypershell-hash-components`** — the checksum extension, on `sha2` and `hex`.
- **`hypershell-tungstenite-components`** — the WebSocket extension, on `tokio-tungstenite`.
- **`hypershell-macro`** — the `hypershell!` macro.
- **`hypershell`** — `HypershellNamespace`, the error wiring, the `HypershellCli` and `HypershellHttp`
  contexts, and the prelude.
- **`hypershell-examples`** — the runnable examples, the four tests, and a small library adding
  `Compare` and `If` and the extension namespaces.

## Status and gaps

Every example with a confirmed run works. `rust_playground` was not run, because running it
publishes a public gist, and `compare_and_branch` has no confirmed run; see
[the examples](examples/README.md). The source is a reliable reference for current
CGP, but the library is a proof of concept with gaps, each confirmed against the `v0.8.0` branch.
[issues.md](issues.md) records them in full, together with the housekeeping items this summary leaves
out:

- **Unusable syntax** — `StreamToLines` has a provider but no route, and its output could not feed a
  later stage even if routed.
- **Silent failures** — a streaming command's exit status and standard error are ignored, and a failed
  WebSocket connection panics.
- **Redirects** — a streaming HTTP request with a reader input sends it as a streamed body, which
  `reqwest` cannot resend, so it does not follow a 301, 302, 307, or 308. A byte-buffer input is sent
  buffered and follows it.
- **Overrides** — a context that joins `HypershellNamespace` cannot reinterpret a syntax the namespace
  already binds; it must use `Use` in the program or restate the routes in its own namespace.
- **The macro** — its expansion needs the prelude in scope, and it panics on unbalanced angle brackets.
- **Evidence** — four tests, two of which assert nothing; no wiring checks; no rustdoc; no CI; and a
  workspace that builds only beside a local `cgp` checkout, on nightly with the new trait solver.

## The documents

The section follows the project shape in [../AGENTS.md](../AGENTS.md#the-shape-of-a-project-section).
Start with the architecture for the ideas every piece shares, then use the reference to look up an
item, and the examples to see a program run.

- [architecture/](architecture/README.md) — the design on one page, and one document per idea:
  - [abstract-syntax.md](architecture/abstract-syntax.md) — programs as types, the four kinds of
    syntax, the internal core syntax, and the macro layer.
  - [interpretation.md](architecture/interpretation.md) — `Handler` as the interpreter, the extractor
    and updater components, calling back into the context, and recursion over type-level lists.
  - [assembly.md](architecture/assembly.md) — backend bundles, the namespace, one-line contexts, and a
    lookup traced through all three.
  - [streams-and-input-dispatch.md](architecture/streams-and-input-dispatch.md) — the stream wrappers,
    two-segment keys that dispatch on the input, the built-in adapters, and which stage accepts what.
  - [error-handling.md](architecture/error-handling.md) — abstract errors in providers, the anyhow
    wiring in the namespace, and registering a new error type.
  - [crate-layout.md](architecture/crate-layout.md) — the crates and their dependency graph, the
    prelude, and the toolchain.
- [reference/](reference/README.md) — every public item, grouped by family, with tables of all
  syntax, components, and providers:
  - [execution.md](reference/execution.md) — `SimpleExec`, `StreamingExec`, `CoreExec`, the command
    updater, and the execution errors.
  - [arguments.md](reference/arguments.md) — the extractors, `StaticArg`, `FieldArg`, `JoinArgs`, and
    `UrlEncodeArg`.
  - [http.md](reference/http.md) — the request syntax, methods, headers, the client getter, and
    `ErrorResponse`.
  - [streams-and-io.md](reference/streams-and-io.md) — the conversions, files, standard output, the
    wrappers, the adapters, and the input dispatchers.
  - [json.md](reference/json.md) — `EncodeJson` and `DecodeJson`.
  - [control.md](reference/control.md) — `Pipe`, `Call`, `Use`, `ConvertTo`, `Box`, and
    `ReturnInput`.
  - [extensions.md](reference/extensions.md) — the checksum and WebSocket crates.
  - [contexts-and-namespace.md](reference/contexts-and-namespace.md) — the namespace's full route
    table, the error aggregate, the bundles, the contexts, and the prelude.
  - [macro.md](reference/macro.md) — the rules of `hypershell!` and its edges.
- [examples/](examples/README.md) — each runnable program in the repository, what it needs, and
  whether it works, plus the examples library's `Compare` and `If`.
- [guides/](guides/README.md) — how to do one job:
  - [writing-a-program.md](guides/writing-a-program.md) — using the language, from choosing a context
    to checking a program.
  - [extending-the-language.md](guides/extending-the-language.md) — adding syntax, error types, and
    extension namespaces, and replacing an interpretation.
  - [debugging.md](guides/debugging.md) — the common mistakes with their code and `cargo cgp check`
    output.
- [testing.md](testing.md) — what the four tests pin, what the examples add, and what nothing
  exercises.
- [issues.md](issues.md) — the confirmed defects, missing features, and housekeeping items.

## Public material derived from these documents

These documents are the source for the project's public writing, and each one names what it feeds.
Three artifacts are planned:

- **The Hypershell deep dive** on the website, specified in
  [website/deep-dives/hypershell.md](../../website/deep-dives/hypershell.md). Its pages draw on the
  architecture for programs as types, interpretation, and assembly; on the guides and examples for
  extension; and on the issues and testing documents for the trade-offs page.
- **The repository README**, which pins `cgp` 0.4.1 in its install snippet, still speaks of presets,
  and defers to the announcement post for everything else.
- **Rustdoc for every public item.** The source carries no doc comments, so the crates' docs.rs pages
  list items without explanation; the reference entries are written to be condensed into them.

## How it relates to the rest of the base

The [shell-scripting DSL example](../../examples/shell-scripting-dsl.md) develops the project's
scenario as a teaching progression, building on these crates, and is the source other documents
quote. The [announcement post](../../website/blog/hypershell-release.md) is the fullest published
account, but its wiring code predates four breaking releases; its document records what has drifted.
**Do not take current syntax from it.** The project also appears on the website's
[Resources page](../../website/site-structure.md), and the
[communication strategy](../../communication-strategy/evidence.md) counts it as social proof for the
evaluator profile.

On the CGP side, Hypershell is the reference implementation of
[type-level DSLs](../../cgp/concepts/type-level-dsls.md), and the reason the
[handler family](../../cgp/concepts/handlers.md) exists: the family was introduced in CGP v0.4.1 for
this project. Its interpreter is [`Handler`](../../cgp/reference/components/handler.md); its providers
are written with [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) and draw on the context
through [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md); its errors follow
[modular error handling](../../cgp/concepts/modular-error-handling.md); its pipelines use
[`PipeHandlers`](../../cgp/reference/providers/handler_combinators.md); and its assembly uses
[namespaces](../../cgp/concepts/namespaces.md), [`#[prefix]`](../../cgp/reference/attributes/prefix.md),
[aggregate providers](../../cgp/concepts/aggregate-providers.md), and the `open` statement of
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md). It is also the largest
user of dispatch on a component's second parameter through a path key, documented under
[`RedirectLookup`](../../cgp/reference/providers/redirect_lookup.md) and
[dispatching per type](../../cgp/guides/dispatching-per-type.md).
