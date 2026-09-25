# Interpretation

Hypershell interprets a program by resolving CGP components for it, one provider per piece of
syntax, with composite syntax interpreted by calling back into the same context. This document
covers the components that do the interpreting, how a provider matches its syntax and declares what
it needs, and the three ways a provider hands work back to the context. The general pattern is
[type-level DSLs](../../../cgp/concepts/type-level-dsls.md); the providers are listed in the
[reference](../reference/README.md).

## `Handler` is the interpreter interface

**Running a program is one call to `CanHandle::handle`, with the program as the `Code` tag and the
program's input as the argument.** Hypershell defines no interpreter trait of its own. It uses
CGP's [`Handler`](../../../cgp/reference/components/handler.md) component, the async and fallible
member of the [handler family](../../../cgp/concepts/handlers.md):

```rust
let output = app.handle(PhantomData::<Program>, input).await?;
```

`Code` is the program or program fragment, `Input` is the data flowing in, and the associated
`Output` is what the fragment produces. Because `Output` is determined by the provider that answers
for a given `Code` and `Input`, the output type of a whole program is computed by the compiler from
the wiring. Only the input type is chosen at the call site. A `Vec<u8>` or `String` input is the
standard input of the first stage. A program that starts with `ReadFile` takes `()`, and one that
starts with `EncodeJson` takes any `Serialize` value.

## A provider matches one shape of syntax

**An interpreter is a `Handler` provider whose impl header pattern-matches the `Code` parameter.**
`HandleSimpleExec` implements `Handler` only when `Code` has the shape
`SimpleExec<CommandPath, Args>`, which binds the two inner parameters for use in its bounds:

```rust
#[cgp_impl(new HandleSimpleExec)]
impl<Context, CommandPath, Args, Input> Handler<SimpleExec<CommandPath, Args>, Input> for Context
where
    Context: CanHandle<CoreExec<CommandPath, Args>, (), Output = Child>
        + for<'a> CanRaiseError<ExecOutputError>
        + CanWrapError<StdinPipeError>
        + CanWrapError<WaitWithOutputError>
        + CanRaiseError<std::io::Error>,
    Input: Send + AsRef<[u8]>,
{
    type Output = Vec<u8>;

    async fn handle(/* … */) -> Result<Vec<u8>, Context::Error> { /* … */ }
}
```

Everything the provider needs from the context is in the `where` clause, as
[impl-side dependencies](../../../cgp/concepts/impl-side-dependencies.md): a way to spawn the
process, and a way to raise and wrap each error it can produce. None of it appears on the `Handler`
interface, so a context that never runs `SimpleExec` never has to satisfy it. The `Input` bound is
also a dependency. It is what decides which stage can follow which; see
[streams-and-input-dispatch.md](streams-and-input-dispatch.md).

A provider may also ignore the syntax entirely. The stream adapters and `HandleBytesToHex` implement
`Handler<Code, Input>` for every `Code`, since they take no information from it, and the wiring
decides which syntax they answer for.

**Providers are written in the explicit form of [`#[cgp_impl]`](../../../cgp/reference/macros/cgp_impl.md).**
Almost every provider names the context (`impl<Context, …> Handler<…> for Context`) and lists its
dependencies as `Context:` bounds. None uses [`#[uses]`](../../../cgp/reference/attributes/uses.md),
and only `BoxHandler` and `DecodeUtf8Bytes` use [`#[use_type]`](../../../cgp/reference/attributes/use_type.md).
This is valid, but it is not the form the [writing-providers](../../../cgp/guides/writing-providers.md)
and [declaring-dependencies](../../../cgp/guides/declaring-dependencies.md) guides recommend; the
modernization is tracked in [issues.md](../issues.md#housekeeping).

## Arguments have their own components

**Argument syntax is interpreted by four extractor components, not by `Handler`.** An argument is
not a pipeline stage: it has no input and produces a value synchronously. Each extractor is a
component generic over the argument syntax `Arg`, defined in
[`hypershell-components/src/components/`](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-components/src/components):

| Consumer trait | Produces | Used for |
|---|---|---|
| `CanExtractStringArg<Arg>` | `Cow<'_, str>` | header names and values, WebSocket URLs, and as the base of the others |
| `CanExtractCommandArg<Arg>` | the abstract `CommandArg` type | command paths, command arguments, file paths |
| `CanExtractUrlArg<Arg>` | the abstract `Url` type, fallibly | HTTP request URLs |
| `CanExtractMethodArg<Arg>` | the abstract `HttpMethod` type | HTTP methods |

The three non-string extractors return [abstract types](../../../cgp/concepts/abstract-types.md)
declared with [`#[cgp_type]`](../../../cgp/reference/macros/cgp_type.md): `HasCommandArgType`,
`HasUrlType`, and `HasHttpMethodType`. The components crate never names a concrete type for them.
The backend bundles fix them with `UseType`: `PathBuf` for `CommandArg` in the Tokio bundle, and
`url::Url` and `reqwest::Method` in the reqwest bundle.

The extractors are layered on the string extractor. `ExtractStringCommandArg` handles any argument
by extracting it as a string and converting it with `From<String>`, and `ExtractStringUrlArg` does
the same and then parses it with `FromStr`, raising the parse error. So a new argument syntax that
produces a string becomes usable as a command argument and a URL by adding one string-extractor
entry and routing it to the two layered providers. The exception is `JoinArgs`, which the command
extractor routes to its own `JoinExtractArgs` so that joined path segments go through
`PathBuf::join` rather than concatenation.

**Argument lists are applied by two updater components that mutate a backend's builder.**
`CanUpdateCommand<Args>` in the Tokio crate takes `&mut tokio::process::Command`, and
`CanUpdateRequestBuilder<Args>` in the reqwest crate takes and returns a `reqwest::RequestBuilder`.
These interfaces are deliberately tied to one backend. The coupling does not spread, because only the
providers that use a Tokio `Command` depend on `CanUpdateCommand`, and a context that never runs a
process never needs it.

## Calling back into the context

A provider rarely does all of the work for its syntax. It hands the parts it does not own back to
the context in one of three ways, and each keeps the context's wiring in charge of the part it hands
over.

**A handler calls the context for an internal step.** `HandleSimpleExec` and `HandleStreamingExec`
both obtain a spawned `Child` with `context.handle(PhantomData::<CoreExec<…>>, ())`, and the two
HTTP handlers obtain a `Response` from `CoreHttpRequest` the same way. The step is a piece of
[internal syntax](abstract-syntax.md#internal-syntax-that-users-never-write), so a context can
replace how every command is spawned by rewiring one entry.

**An extractor or updater calls the context for each inner argument.** `ExtractStringCommandArg`
calls `context.extract_string_arg` for whatever argument it was given, and `UpdateRequestHeader`
extracts both the key and the value through the context. An argument expression is therefore
interpreted by the context's wiring at every level of nesting, so `UrlEncodeArg<FieldArg<"org">>`
works because both layers resolve through the context.

**`Call<InCode>` turns one piece of syntax into another.** `Call` is a `Handler` provider that
answers for any `Code` by handling `InCode` on the context instead:

```rust
#[cgp_impl(new Call<InCode>)]
impl<OutCode, InCode, Input, Output> Handler<OutCode, Input>
where
    Self: CanHandle<InCode, Input, Output = Output>,
{
    type Output = Output;
    // … self.handle(PhantomData::<InCode>, input).await
}
```

It is how a pipeline's stages are resolved, below, and how the WebSocket bundle converts a byte
input into a stream: its `Vec<u8>` branch starts with `Call<BytesToStream>`, which runs whatever the
context wires for `BytesToStream`. A consequence is that such a provider silently depends on the
context routing the syntax it calls. The WebSocket bundle works under `HypershellNamespace` because
the namespace routes `BytesToStream`.

## Recursion over type-level lists

**A provider for a list syntax is one struct with two impls, one for `Cons` and one for `Nil`, and
the `Cons` impl handles the head and recurses on the tail.** `JoinArgs` is interpreted this way by
`JoinStringArgs`:

```rust
pub struct JoinStringArgs;

#[cgp_impl(JoinStringArgs)]
impl<Context, Arg, Args> StringArgExtractor<JoinArgs<Cons<Arg, Args>>> for Context
where
    Context: CanExtractStringArg<Arg>,
    JoinStringArgs: StringArgExtractor<Context, JoinArgs<Args>>,
{ /* extract the head through the context, then call JoinStringArgs for the tail */ }

#[cgp_impl(JoinStringArgs)]
impl<Context> StringArgExtractor<JoinArgs<Nil>> for Context { /* the empty string */ }
```

The struct is declared by hand and each impl names it without `new`, since two impls share it. The
head is resolved through the context, so each element may be any argument syntax the context
routes. The tail is resolved through the provider itself, named in the `where` clause, so the
recursion never re-enters the wiring for the list. `JoinExtractArgs` and `UpdateRequestHeaders`
follow the same pattern for `JoinArgs` as a path and for `WithHeaders`.

`ExtractArgs`, which interprets `WithArgs`, recurses differently. It writes the tail bound as
`Self: CommandUpdater<Context, WithArgs<Args>>`, and `#[cgp_impl]` reads `Self` as the context, so the
bound expands to `Context: CommandUpdater<Context, WithArgs<Args>>` and the tail call to
`Context::update_command`. Each tail is therefore looked up again through the context's wiring, and
the recursion works only because the namespace routes every `WithArgs<Args>` back to `ExtractArgs`.
The inconsistency is recorded in [issues.md](../issues.md#housekeeping).

## Control syntax

The control syntax is interpreted by small providers in the components crate, routed through the
base bundle described in [assembly.md](assembly.md).

**`Pipe<Handlers>` becomes CGP's `PipeHandlers` over one `Call` per stage.** The `HandlePipe`
aggregate maps `Pipe<Handlers>` to `PipeHandlers<Handlers::Wrapped>`, where the `WrapCall` trait
rewrites `Product![A, B, C]` into `Product![Call<A>, Call<B>, Call<C>]`. The
[handler combinator](../../../cgp/reference/providers/handler_combinators.md) then threads each
stage's output into the next stage's input, and every stage is resolved through the context.
`HandlePipe` still does this with a legacy [`UseDelegate`](../../../cgp/reference/providers/use_delegate.md)
nested table, because its key carries a bound (`<Handlers: WrapCall> Pipe<Handlers>`). A probe
confirmed that the `open` statement accepts the same bounded key, so the table can be converted; see
[issues.md](../issues.md#housekeeping).

**`Use<Provider, Code>` runs a provider named in the program.** `HandleUseProvider` forwards to
`Provider::handle` with `Code` (default `()`), bypassing the context's wiring for that one stage. It
lets a program name an interpreter that no namespace routes.

**`Box<Code>` runs `Code` behind a boxed future.** The base bundle maps `Box<Code>` to
`BoxHandler<Call<Code>>`, and `BoxHandler` pins the inner provider's future in a
`Pin<Box<dyn Future>>`. It requires the code, the input, and the inner provider to be `'static`. The
examples crate uses `BoxHandler` directly for its `Compare` syntax, with a comment that the
comparison is much slower without boxing; the comment does not say whether it means compile time or
run time.

**`ConvertTo<T>` is wired but never resolves.** The base bundle maps it to `Promote<HandleConvert>`,
and `HandleConvert` implements only `Computer`, while `Promote`'s `Handler` impl requires an
`AsyncComputer`. A probe confirms the failure; see [issues.md](../issues.md#convertto-never-resolves).

## Source

- The components: [crates/hypershell-components/src/components/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-components/src/components), [crates/hypershell-tokio-components/src/components/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tokio-components/src/components), and [crates/hypershell-reqwest-components/src/components/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-reqwest-components/src/components)
- The control providers: [crates/hypershell-components/src/providers/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-components/src/providers)
- `WrapCall`: [crates/hypershell-components/src/traits/wrap_call.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/traits/wrap_call.rs)
- `HandleSimpleExec` and `ExtractArgs`: [crates/hypershell-tokio-components/src/providers/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tokio-components/src/providers)

## Public material derived from this

Page 2, "Interpreting a program", of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
