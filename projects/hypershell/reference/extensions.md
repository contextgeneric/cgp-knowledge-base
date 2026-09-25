# Extension crates

Two crates extend the language without being part of the assembled `hypershell` crate:
`hypershell-hash-components` adds native checksums, and `hypershell-tungstenite-components` adds
WebSockets. Neither is routed by `HypershellNamespace`, so a context gains them through an extension
namespace or its own entries; see [extending the language](../guides/extending-the-language.md).

## `Checksum` and `HandleStreamChecksum`

`Checksum<Hasher>` computes a digest of its input stream with any `sha2::Digest` implementation.

### Definition

```rust
pub struct Checksum<Hasher>(pub PhantomData<Hasher>);

#[cgp_impl(new HandleStreamChecksum)]
impl<Context, Input, Hasher> Handler<Checksum<Hasher>, Input> for Context
where
    Context: CanRaiseError<Input::Error>,
    Input: Unpin + TryStream,
    Hasher: Digest,
    Input::Ok: AsRef<[u8]>,
{
    type Output = GenericArray<u8, Hasher::OutputSize>;
    // ...
}
```

### Behavior

The provider folds every chunk of a `TryStream` into the hasher and returns the finished digest as a
fixed-size byte array, raising the stream's own error type. It covers every hash algorithm with one
impl, since `Hasher` is any `Digest`, and a program names the algorithm type directly, as in
`Checksum<sha2::Sha256>`, which makes `sha2` a dependency of the program. The digest is raw bytes, so
a program that prints it follows it with `BytesToHex`. Under the examples crate's wiring the syntax
is a two-stage pipeline, `PipeHandlers<Product![HandleToFuturesStream, HandleStreamChecksum]>`, so it
accepts bytes or either reader wrapper. With a streaming HTTP input, the stream error is
`std::io::Error`, which the namespace already routes.

### Context dependencies

Raising the input stream's error type.

## `BytesToHex` and `HandleBytesToHex`

`BytesToHex` encodes byte-like input as a lowercase hexadecimal string.

### Definition

```rust
pub struct BytesToHex;

#[cgp_impl(new HandleBytesToHex)]
impl<Context, Code, Input> Handler<Code, Input> for Context
where
    Context: HasErrorType,
    Input: AsRef<[u8]>,
{
    type Output = String;
    // ...
}
```

### Behavior

The provider calls `hex::encode` and cannot fail. It ignores the `Code`, so it can answer for any
syntax a bundle routes to it. Through it, `http_checksum_native` prints the same digest that
`sha256sum` produces in the other two checksum examples.

## `WebSocket` and `HandleWebsocket`

`WebSocket<Url, Params>` connects to a WebSocket server, sends its input stream as binary messages,
and produces the received messages as a stream.

### Definition

```rust
pub struct WebSocket<Url, Params>(pub PhantomData<(Url, Params)>);

#[cgp_impl(new HandleWebsocket)]
impl<Context, UrlArg, Headers, Input> Handler<WebSocket<UrlArg, Headers>, Input> for Context
where
    Context: CanExtractStringArg<UrlArg> + CanRaiseError<tungstenite::Error>,
    Input: Send + AsyncRead + Unpin + 'static,
{
    type Output = Pin<Box<dyn FuturesAsyncRead + Send>>;
    // ...
}
```

### Behavior

The syntax type lives in `hypershell-components`; the provider and its bundle live in the tungstenite
crate. The URL is a string argument, not a URL argument, so it is not parsed by `url`. The provider
connects with `tokio_tungstenite::connect_async`, spawns a Tokio task that forwards the input to the
socket as binary messages, and returns a reader over the incoming messages. A text message is
emitted with a trailing newline, and any other message as its raw payload. When the input ends, the
forwarding task closes the socket, which is why the `bluesky_websocket` example passes a reader over
a pipe it never writes.

`HypershellTungsteniteProvider` wires one pipeline per input kind under the same syntax, keyed on
both segments of the path:

- **`FuturesAsyncReadStream<S>`** — `FuturesToTokioAsyncRead`, then `HandleWebsocket`, then
  `WrapFuturesAsyncRead`.
- **`TokioAsyncReadStream<S>`** — `HandleWebsocket`, then `WrapFuturesAsyncRead`.
- **`Vec<u8>`** — `Call<BytesToStream>`, then `HandleWebsocket`, then `WrapFuturesAsyncRead`.

The output is a futures reader, so `StreamToString` needs `ToTokioAsyncRead` before it, while
`StreamingExec` and `StreamToStdout` accept it directly.

### Context dependencies

The string extractor for the URL, raising `tungstenite::Error`, and, for the `Vec<u8>` branch, a
route for `BytesToStream`.

### Known issues

A connection failure panics: the provider calls `unwrap()` on `connect_async`, and a probe against a
refused port panicked with `called Result::unwrap() on an Err value: Io(… ConnectionRefused …)`.
The `Params` parameter is ignored, so headers cannot be set, and `String` input is not wired. See
[issues.md](../issues.md#the-websocket-handler-panics-on-a-failed-connection).

## Wiring

The hash crate ships no bundle. `HypershellChecksumProvider` in the examples crate wires `Checksum`
and `BytesToHex`, and `HypershellChecksumNamespace` routes both; see the
[examples crate](../examples/README.md#the-examples-library). The tungstenite crate ships
`HypershellTungsteniteProvider`, and a context routes `WebSocket` to it with an entry of its own, as
[`bluesky_websocket`](../examples/bluesky-websocket.md) does. That context must also route
`tungstenite::Error` to a raiser.

## Source

- [crates/hypershell-hash-components/src/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-hash-components/src)
- [crates/hypershell-tungstenite-components/src/providers/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tungstenite-components/src/providers)
- [crates/hypershell-components/src/dsl/http.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/http.rs) (the `WebSocket` syntax)

## Public material derived from this

Rustdoc for the extension crates, and page 4, "Extending the language", of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
