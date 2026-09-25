# Hypershell architecture

Hypershell is built from a handful of design decisions that every syntax type and provider in it
follows. This page states them together so a reader can hold the whole design at once before opening
the reference. Each decision has its own document below, which carries the mechanism and the code;
this page carries only the claim and why it matters. CGP's own constructs are documented under
[cgp/](../../../cgp/README.md) and are linked rather than re-explained, per
[../../AGENTS.md](../../AGENTS.md#leave-cgp-itself-to-cgp).

## The design on one page

**A program is a type, and every piece of syntax is an empty marker struct.** `SimpleExec<Path, Args>`,
`StreamToStdout`, and `FieldArg<Tag>` hold nothing but `PhantomData`, and none of them has an impl
of its own. A pipeline is a `Pipe` over a [`Product!`](../../../cgp/reference/macros/product.md)
list of stages, and a string literal inside a program is a
[`Symbol!`](../../../cgp/reference/macros/symbol.md). The `hypershell!` macro is a thin token rewriter
over this abstract syntax and carries no meaning of its own. Because the syntax says nothing about
behavior, what a program does is decided entirely by the context that runs it. See
[abstract-syntax.md](abstract-syntax.md).

**Running a program is resolving one component, and each provider interprets one piece of syntax.**
The interpreter interface is CGP's [`Handler`](../../../cgp/reference/components/handler.md)
component: `context.handle(PhantomData::<Program>, input)`. A provider such as `HandleSimpleExec`
implements `Handler` for one syntax shape by matching the `Code` parameter, and states what it needs
from the context as [impl-side dependencies](../../../cgp/concepts/impl-side-dependencies.md). The
arguments inside a syntax are a small second language of their own, interpreted by four extractor
components rather than by `Handler`. Composite syntax is interpreted by calling back into the
context, so a pipeline stage, a command's arguments, or an internal "core" step is resolved through
the same wiring as the program itself. See [interpretation.md](interpretation.md).

**The language is assembled in three wiring layers.** Each backend crate publishes an
[aggregate provider](../../../cgp/concepts/aggregate-providers.md), such as
`HypershellTokioProvider`, whose table `open`s the components it serves and maps each syntax to the
provider that interprets it. `HypershellNamespace`, defined with
[`cgp_namespace!`](../../../cgp/reference/macros/cgp_namespace.md), routes groups of syntax to those
bundles under the path prefixes the components register with
[`#[prefix]`](../../../cgp/reference/attributes/prefix.md). A context then joins the namespace in one
statement, and `HypershellCli` is nothing more than that statement. See [assembly.md](assembly.md).

**Streams carry distinct wrapper types, and handlers dispatch on the input type through the same
path mechanism as on the syntax.** A stage's output is its next stage's input, so the input type
decides which provider can run. The `open` redirect appends every parameter of
`CanHandle<Code, Input>` to the lookup path, so a key such as
`@HandlerComponent.<Code> Code.<S> TokioAsyncReadStream<S>` dispatches on the input while ignoring
the syntax. Hypershell wraps each stream kind in its own
newtype so those keys never overlap, and composes adapters into a syntax's own wiring so that most
stages accept bytes or any stream kind. See
[streams-and-input-dispatch.md](streams-and-input-dispatch.md).

**Errors are abstract in every provider and concrete only in the namespace.** Providers name
[`CanRaiseError`](../../../cgp/reference/components/can_raise_error.md) and `CanWrapError` for each
source error and detail they produce, and never name `anyhow`. `HypershellNamespace` fixes the error
type to `anyhow::Error` and routes each source error type to a raising strategy through one
aggregate, `HypershellErrorHandler`. An extension that raises a new error type must register it. See
[error-handling.md](error-handling.md).

**Crates split along backends, so a crate compiles only what it interprets.** The syntax and the
component interfaces live in `hypershell-components`, which depends only on `cgp`. Each backend crate
adds one external library: Tokio for processes and files, `reqwest` for HTTP, `serde_json` for JSON,
`sha2` and `hex` for checksums, `tokio-tungstenite` for WebSockets. The assembly crate `hypershell`
names concrete types last. See [crate-layout.md](crate-layout.md).

## The catalog

Register each architecture document here, in [../README.md](../README.md), and in
[../../../summary.md](../../../summary.md) in the same change.

- [abstract-syntax.md](abstract-syntax.md) — programs as types: the handler syntax, the argument
  sub-language, the internal core syntax, the control syntax, and the `hypershell!` surface layer.
- [interpretation.md](interpretation.md) — `Handler` as the interpreter, the four extractor
  components and the two updaters, providers that call back into the context, `Call`, and recursion
  over type-level lists.
- [assembly.md](assembly.md) — the three wiring layers, the prefix scheme, why the backend bundles
  `open` their components, and one lookup traced from `HypershellCli` to `HandleSimpleExec`.
- [streams-and-input-dispatch.md](streams-and-input-dispatch.md) — the stream wrapper types,
  two-segment `Code.Input` keys, the adapter handlers, pipelines built inside one syntax's wiring, and
  how stage types must line up.
- [error-handling.md](error-handling.md) — the anyhow backend, the raising aggregate, error details
  that borrow, and what an extension must register.
- [crate-layout.md](crate-layout.md) — the nine crates and their dependency graph, module layout,
  `no_std` status, and the toolchain facts.

## Public material derived from this

The pages on programs as types, interpretation, and assembly in the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md), and the opening of the repository
README.
