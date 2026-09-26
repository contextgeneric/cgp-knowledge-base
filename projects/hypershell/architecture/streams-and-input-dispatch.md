# Streams and input dispatch

A Hypershell pipeline is typed end to end: each stage's output is its next stage's input, so the
input type decides which provider can run a stage. This document explains the stream types stages
exchange, how a bundle dispatches on the input type through the same path mechanism it uses for the
syntax, and how adapters are built into a syntax's wiring so that most stages accept several input
kinds. The CGP mechanisms are the `open` statement of
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md) and
[`PipeHandlers`](../../../cgp/reference/providers/handler_combinators.md).

## What stages exchange

**Stages exchange either a byte buffer or a stream, and a stream always arrives in one of three
wrapper types.** The simple stages (`SimpleExec`, `SimpleHttpRequest`, `EncodeJson`, `BytesToHex`)
produce or consume bytes: a `Vec<u8>`, a `String`, or anything `AsRef<[u8]>`. The streaming stages
produce a stream, and Hypershell wraps each kind of stream in a newtype defined in
[`hypershell-tokio-components/src/types/`](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tokio-components/src/types):

| Wrapper | Wraps | Produced by |
|---|---|---|
| `TokioAsyncReadStream<S>` | a `tokio::io::AsyncRead` | `StreamingExec`, `ReadFile`, `BytesToStream` |
| `FuturesAsyncReadStream<S>` | a `futures::io::AsyncRead` | `StreamingHttpRequest`, `WebSocket` |
| `FuturesStream<S>` | a `futures::Stream` | the adapters feeding `Checksum` |

Each wrapper forwards its trait to the inner value and does nothing else. It exists to give the
three stream kinds distinct *types*, which the next section needs.

## Dispatching on the input type

**The `open` redirect appends every parameter of `CanHandle<Code, Input>` to the lookup path, so a
bundle entry can key on the input as a second segment.** An entry keyed on the syntax alone, such as
`@HandlerComponent.<Path, Args> SimpleExec<Path, Args>`, ends in an open wildcard and matches that
syntax with any input. An entry that continues with a second segment matches only that input. The
input dispatcher `HandleToTokioAsyncRead` is a bundle of such entries, with a generic first segment
so that it ignores the syntax:

```rust
delegate_components! {
    new HandleToTokioAsyncRead {
        open HandlerComponent;

        @HandlerComponent
            .<Code> Code
            .<S> FuturesAsyncReadStream<S>:
                FuturesToTokioAsyncRead,
        @HandlerComponent
            .<Code> Code
            .<S> TokioAsyncReadStream<S>:
                ReturnInput,
        @HandlerComponent
            .<Code> Code.[
                Vec<u8>,
                String,
            ]:
                HandleBytesToTokioAsyncRead,
    }
}
```

Whatever syntax it is asked for, `HandleToTokioAsyncRead` converts a futures reader, a Tokio reader,
or a byte buffer into a Tokio reader, and fails to resolve for any other input type. This is the
mechanism the wrapper types exist for. A key such as `<S: AsyncRead> S` would overlap every other
entry and conflict, while `TokioAsyncReadStream<S>` and `FuturesAsyncReadStream<S>` are distinct
type constructors, so the entries coexist.

The same form dispatches on the syntax *and* the input at once. The WebSocket bundle wires one
pipeline per input kind under the same syntax:

```rust
@HandlerComponent
    .<Url, Params> WebSocket<Url, Params>
    .<S> TokioAsyncReadStream<S>:
        PipeHandlers<Product![HandleWebsocket, WrapFuturesAsyncRead]>,

@HandlerComponent
    .<Url, Params> WebSocket<Url, Params>
    .Vec<u8>:
        PipeHandlers<Product![Call<BytesToStream>, HandleWebsocket, WrapFuturesAsyncRead]>,
```

The mechanism belongs to CGP rather than to Hypershell, and is documented under
[`RedirectLookup`](../../../cgp/reference/providers/redirect_lookup.md) and
[dispatching per type](../../../cgp/guides/dispatching-per-type.md). It replaces the
`UseInputDelegate` nested tables for this job, so no Hypershell component needs the
`#[derive_delegate(UseInputDelegate<…>)]` attribute. One constraint follows from the wildcard.
Within one table, a syntax is keyed either on its own or per input, never both, because the
one-segment key's wildcard covers every two-segment key beneath it and the two impls conflict.

## Adapters built into a syntax's wiring

**Most streaming syntax is wired to a `PipeHandlers` that starts with an input dispatcher, so the
stage accepts bytes or any stream kind without the program saying so.** The Tokio bundle wires
`StreamingExec` as three providers composed end to end:

```rust
@HandlerComponent.<Path, Args> StreamingExec<Path, Args>:
    PipeHandlers<Product![
        HandleToTokioAsyncRead,   // any accepted input → a Tokio reader
        HandleStreamingExec,      // the reader becomes the child's stdin
        WrapTokioAsyncRead,       // the child's stdout → TokioAsyncReadStream
    ]>,
```

The first provider normalizes the input, the middle one does the work, and the last one wraps the
output so the *next* stage can dispatch on it. `WriteFile`, `StreamToStdout`, and `WebSocket` follow
the same shape. `Checksum` starts with the other dispatcher, `HandleToFuturesStream`, which converts
the same inputs into a `FuturesStream`. `StreamingHttpRequest` is keyed per input in its bundle
instead: its reader inputs take this shape, while a `Vec<u8>` or `String` skips the dispatcher and is
sent as a buffered body, which `reqwest` can resend when it follows a redirect; see
[HTTP](../reference/http.md#streaminghttprequest-and-handlestreaminghttprequest).

The effect is that each accepting stage lists the input kinds it handles in its dispatcher, and a
probe confirms the boundary is exact. `StreamingExec` accepts `Vec<u8>`, `String`,
`TokioAsyncReadStream`, and `FuturesAsyncReadStream`. Given a `&'static str`, it fails with a
[`[CGP-E110]`](../../../cargo-cgp/error-code.md) root cause,
`` provider `HandleToTokioAsyncRead` does not contain any delegate entry for `@HandlerComponent.StreamingExec<…>.&str` ``.

## Which stages accept which inputs

**Not every stage has an input dispatcher, and the ones without one are where pipelines fail to
compile.** The table records what each handler syntax accepts under `HypershellNamespace`:

| Syntax | Accepts | Produces |
|---|---|---|
| `SimpleExec` | anything `Send + AsRef<[u8]>` | `Vec<u8>` |
| `StreamingExec` | `Vec<u8>`, `String`, either reader wrapper | `TokioAsyncReadStream` |
| `SimpleHttpRequest` | anything `Into<reqwest::Body>` | `Vec<u8>` |
| `StreamingHttpRequest` | `Vec<u8>`, `String`, either reader wrapper | `FuturesAsyncReadStream` |
| `ReadFile` | `()` only | `TokioAsyncReadStream<File>` |
| `WriteFile` | `Vec<u8>`, `String`, either reader wrapper | `()` |
| `StreamToStdout` | `Vec<u8>`, `String`, either reader wrapper | `()` |
| `StreamToBytes`, `StreamToString` | any `tokio::io::AsyncRead + Unpin`, which among stage outputs is `TokioAsyncReadStream` only | `Vec<u8>`, `String` |
| `BytesToStream` | anything `AsRef<[u8]> + Unpin` | `TokioAsyncReadStream` |
| `BytesToString` | anything `AsRef<[u8]>` | `String` |
| `EncodeJson` | anything `Serialize` | `Vec<u8>` |
| `DecodeJson<T>` | anything `AsRef<[u8]>` | `T` |
| `Checksum<Hasher>` | `Vec<u8>`, `String`, either reader wrapper | `GenericArray<u8, …>` |
| `BytesToHex` | anything `AsRef<[u8]>` | `String` |
| `WebSocket` | `Vec<u8>`, either reader wrapper | `FuturesAsyncReadStream` |

Two consequences come up in practice:

- **A streaming stage cannot feed a simple stage directly.** `StreamingExec | SimpleExec` fails with
  `TokioAsyncReadStream<…>: AsRef<[u8]>` unsatisfied. Insert `StreamToBytes` between them.
- **`StreamToBytes` and `StreamToString` accept only Tokio readers.** Placed after
  `StreamingHttpRequest` or `WebSocket`, whose output is a futures reader, they fail to resolve.
  Insert the `ToTokioAsyncRead` adapter syntax first. It is exported from
  `hypershell_tokio_components::dsl`, not from the prelude, and a probe confirms
  `StreamingHttpRequest | ToTokioAsyncRead | StreamToString` works.

The simple stages have no dispatcher because their bound is already generic. `SimpleExec` takes
anything byte-like with one provider and needs no per-type routing.

## How a streaming stage runs

**`StreamingExec` spawns its process and returns its standard output immediately, copying the input
into standard input on a spawned Tokio task.** Stages in a pipeline therefore run concurrently, as in
a shell. **A failure is reported when the stream ends rather than when the stage returns.** The
returned reader, a `ChildOutputStream`, waits for the child at the end of its standard output and
ends with an error if the child exited with a non-success status or if reading its input failed. The
stage reading it raises that error, so a failing command anywhere in a streamed pipeline fails the
program. Standard error is drained while the child runs and becomes part of the error's message; see
[execution](../reference/execution.md#streamingexec-and-handlestreamingexec).

`HandleStreamingExec`'s output stream starts its tasks with `tokio::spawn`, as `HandleWebsocket` does
for its forwarding task, so a program with either stage must run inside a Tokio runtime. All the examples use
`#[tokio::main]`.

## Source

- The wrapper types: [crates/hypershell-tokio-components/src/types/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tokio-components/src/types)
- The dispatchers: [async_read.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/async_read.rs) and [futures_stream.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/futures_stream.rs)
- The adapter providers: [crates/hypershell-tokio-components/src/providers/stream.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/stream.rs)
- The per-input WebSocket wiring: [crates/hypershell-tungstenite-components/src/providers/combined.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tungstenite-components/src/providers/combined.rs)

## Public material derived from this

Page 2 of the planned [Hypershell deep dive](../../../website/deep-dives/hypershell.md), on how
stage types line up, and the input-dispatch example for the website's CGP reference page on the
`open` statement.
