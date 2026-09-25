# Streams and I/O

The streams family is the glue between stages: syntax that converts between bytes and streams, the
file and standard-output stages, the three stream wrapper types, and the adapter providers and input
dispatchers that the other families compose into their wiring. Everything here is in
`hypershell-tokio-components`, except the syntax types and `BytesToString`, which are in
`hypershell-components`. Why the wrappers and dispatchers exist is in
[streams and input dispatch](../architecture/streams-and-input-dispatch.md).

## The conversion syntax

Six syntax types convert one stage's output into another stage's input. Each is a unit struct.

### Definition

```rust
pub struct StreamToBytes;
pub struct StreamToString;
pub struct StreamToStdout;
pub struct BytesToString;
pub struct BytesToStream;
pub struct StreamToLines;
pub struct ConvertTo<T>(pub PhantomData<T>);   // documented in control.md

pub struct ToTokioAsyncRead;                    // hypershell_tokio_components::dsl
```

### Behavior

Each syntax is interpreted by the provider its bundle routes it to:

| Syntax | Provider under the namespace | Accepts | Produces |
|---|---|---|---|
| `StreamToBytes` | `HandleTokioAsyncReadToBytes` | a Tokio reader | `Vec<u8>` |
| `StreamToString` | `HandleTokioAsyncReadToString` | a Tokio reader | `String` |
| `StreamToStdout` | `PipeHandlers<Product![HandleToTokioAsyncRead, HandleStreamToStdout]>` | `Vec<u8>`, `String`, either reader wrapper | `()` |
| `BytesToString` | `DecodeUtf8Bytes` | `AsRef<[u8]>` | `String` |
| `BytesToStream` | `HandleBytesToTokioAsyncRead` | `AsRef<[u8]> + Unpin` | `TokioAsyncReadStream` |
| `ToTokioAsyncRead` | `HandleToTokioAsyncRead` | `Vec<u8>`, `String`, either reader wrapper | `TokioAsyncReadStream` |
| `StreamToLines` | none | — | — |

`StreamToStdout` copies its input to the program's standard output with `tokio::io::copy`, raising
a `std::io::Error` on failure. `BytesToString` decodes UTF-8, raising a `Utf8Error` wrapped with a
`DecodeUtf8InputError` detail that borrows the raw bytes. `ToTokioAsyncRead` is the explicit form of
the input dispatcher, for a program that must put a futures reader in front of a stage that accepts
only Tokio readers:

```rust
StreamingHttpRequest<GetMethod, FieldArg<"url">, WithHeaders[]> | ToTokioAsyncRead | StreamToString
```

### Known issues

`StreamToBytes` and `StreamToString` accept a Tokio reader only, so they cannot follow the HTTP or
WebSocket stages without `ToTokioAsyncRead`, which the prelude does not export. `StreamToLines` has a
provider, `HandleStreamToLines`, but no bundle or namespace route, so a program using it fails to
compile. See [issues.md](../issues.md#defects).

## `ReadFile`, `WriteFile`, and their providers

`ReadFile<Path>` opens a file as a stream, and `WriteFile<Path>` writes its input to a file.

### Definition

```rust
pub struct ReadFile<Path>(pub PhantomData<Path>);

pub struct WriteFile<Path>(pub PhantomData<Path>);

#[cgp_impl(new HandleReadFile)]
impl<Context, PathArg> Handler<ReadFile<PathArg>, ()> for Context
where
    Context: CanExtractCommandArg<PathArg> + CanRaiseError<std::io::Error>,
    Context::CommandArg: AsRef<Path>,
{
    type Output = File;
    // ...
}

#[cgp_impl(new HandleWriteFile)]
impl<Context, PathArg, Input> Handler<WriteFile<PathArg>, Input> for Context
where
    Context: CanExtractCommandArg<PathArg> + CanRaiseError<std::io::Error>,
    Context::CommandArg: AsRef<Path>,
    Input: AsyncRead + Unpin,
{
    type Output = ();
    // ...
}
```

### Behavior

The path is a command argument, so it may be a `StaticArg`, a `FieldArg`, or a `JoinArgs` of
segments joined as a path. `ReadFile` takes `()` as its input, so it must be the first stage of a
program run with `()`; the bundle wraps its `File` output as a `TokioAsyncReadStream`. `WriteFile`
creates or truncates the file and copies the input into it; the bundle puts `HandleToTokioAsyncRead`
in front of it, so it accepts bytes or either reader wrapper. Both raise `std::io::Error`. A probe
wrote and read back a file through `JoinArgs[FieldArg<"dir">, StaticArg<"name">]`.

## The stream wrapper types

`TokioAsyncReadStream<S>`, `FuturesAsyncReadStream<S>`, and `FuturesStream<S>` mark which kind of
stream a stage produced, so the next stage can dispatch on it.

### Definition

```rust
pub struct TokioAsyncReadStream<S> { pub stream: S }
pub struct FuturesAsyncReadStream<S> { pub stream: S }
pub struct FuturesStream<S> { pub stream: S }
```

### Behavior

Each implements `From<S>` and forwards its trait (`tokio::io::AsyncRead`, `futures::io::AsyncRead`,
or `futures::Stream`) to `stream`, all requiring `S: Unpin`. A program's caller may construct one
directly as an input: the `bluesky_websocket` example passes a `TokioAsyncReadStream` over a Tokio
`simplex` pipe that is never written, to keep the WebSocket open.

## The adapter providers

These providers convert between bytes and the stream kinds. Every one implements
`Handler<Code, Input>` for any `Code` and requires only `HasErrorType`, or
`CanRaiseError<std::io::Error>` where it reads.

### Definition

| Provider | Input bound | Output |
|---|---|---|
| `HandleTokioAsyncReadToBytes` | `tokio::io::AsyncRead + Unpin` | `Vec<u8>` |
| `HandleTokioAsyncReadToString` | `tokio::io::AsyncRead + Unpin` | `String` |
| `HandleBytesToTokioAsyncRead` | `AsRef<[u8]> + Unpin` | `TokioAsyncReadStream<Compat<Cursor<Input>>>` |
| `HandleBytesToStream` | `AsRef<[u8]> + Unpin` | `FuturesStream<Iter<Once<Result<Input, Infallible>>>>` |
| `FuturesToTokioAsyncRead` | `futures::io::AsyncRead + Unpin` | `TokioAsyncReadStream<Compat<Input>>` |
| `TokioToFuturesAsyncRead` | `tokio::io::AsyncRead + Unpin` | `FuturesAsyncReadStream<Compat<Input>>` |
| `WrapTokioAsyncRead` | `tokio::io::AsyncRead + Unpin` | `TokioAsyncReadStream<Input>` |
| `WrapFuturesAsyncRead` | `futures::io::AsyncRead + Unpin` | `FuturesAsyncReadStream<Input>` |
| `AsyncReadToStream` | `tokio::io::AsyncRead + Unpin` | `FuturesStream<ReaderStream<Input>>` |
| `HandleStreamToLines` | `tokio::io::AsyncRead + Unpin + 'static` | `Box<dyn Stream<Item = Result<String, LinesCodecError>>>` |

### Behavior

Conversions that read the whole input (`…ToBytes`, `…ToString`) raise `std::io::Error`; the others
cannot fail. The `Wrap…` providers only tag a reader with its wrapper type, and are the last stage of
the pipelines that produce streams.

### Known issues

`TokioToFuturesAsyncRead` and `HandleStreamToLines` are routed nowhere. `HandleStreamToLines`
also returns a `Box<dyn Stream<…>>` with no `Unpin` bound on the trait object. `futures` implements
`Stream` for `Box<S>` only when `S: Unpin`, so the box is not itself a stream a later stage could
consume, and it carries no wrapper type for a dispatcher to match. See
[issues.md](../issues.md#defined-but-unrouted-providers).

## `HandleToTokioAsyncRead` and `HandleToFuturesStream`

These two aggregate providers are the input dispatchers the other families put at the head of their
pipelines.

### Definition

```rust
delegate_components! {
    new HandleToTokioAsyncRead {
        open HandlerComponent;

        @HandlerComponent.<Code> Code.<S> FuturesAsyncReadStream<S>: FuturesToTokioAsyncRead,
        @HandlerComponent.<Code> Code.<S> TokioAsyncReadStream<S>: ReturnInput,
        @HandlerComponent.<Code> Code.[Vec<u8>, String]: HandleBytesToTokioAsyncRead,
    }
}

delegate_components! {
    new HandleToFuturesStream {
        open HandlerComponent;

        @HandlerComponent.<Code> Code.<S> FuturesAsyncReadStream<S>:
            PipeHandlers<Product![FuturesToTokioAsyncRead, AsyncReadToStream]>,
        @HandlerComponent.<Code> Code.<S> TokioAsyncReadStream<S>: AsyncReadToStream,
        @HandlerComponent.<Code> Code.[Vec<u8>, String]: HandleBytesToStream,
    }
}
```

### Behavior

Each dispatches on the input type alone, whatever the syntax, and converts the four accepted inputs
to a Tokio reader or a futures stream. Any other input fails to resolve with a `[CGP-E107]` root
cause naming the dispatcher and the missing `@HandlerComponent.<syntax>.<input>` entry. The
`ReturnInput` here is Hypershell's own provider, documented in [control.md](control.md#returninput).

## Wiring

`HypershellTokioProvider` maps `StreamToBytes`, `StreamToString`, `StreamToStdout`, `BytesToStream`,
`ToTokioAsyncRead`, `ReadFile`, and `WriteFile`; `HypershellBaseProvider` maps `BytesToString`.
`HypershellNamespace` routes all of them.

## Source

- [crates/hypershell-components/src/dsl/convert.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/convert.rs), [file.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/file.rs), and [out.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/out.rs)
- [crates/hypershell-components/src/providers/convert.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/providers/convert.rs)
- [crates/hypershell-tokio-components/src/dsl/stream.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/dsl/stream.rs)
- [crates/hypershell-tokio-components/src/types/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tokio-components/src/types)
- [crates/hypershell-tokio-components/src/providers/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tokio-components/src/providers): `stream.rs`, `file.rs`, `out.rs`, `line.rs`, `async_read.rs`, `futures_stream.rs`

## Public material derived from this

Rustdoc for the stream and I/O items.
