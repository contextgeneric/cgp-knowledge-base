# `bluesky_websocket`

The Bluesky firehose read with the native WebSocket extension instead of `websocat`, wired onto the
context with two entries rather than through an extension namespace.

- **Source**:
  [crates/hypershell-examples/examples/bluesky_websocket.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/bluesky_websocket.rs)
- **Run**: `cargo run --example bluesky_websocket`, stopped with Ctrl-C
- **Needs**: network, `grep`
- **Result**: streams firehose events containing `love` until stopped

## The program

```rust
use cgp::core::error::ErrorRaiserComponent;
use cgp_error_anyhow::RaiseAnyhowError;
use hypershell::namespaces::HypershellNamespace;
use hypershell::prelude::*;
use hypershell_tokio_components::types::TokioAsyncReadStream;
use hypershell_tungstenite_components::providers::HypershellTungsteniteProvider;
use tokio::io::simplex;
use tokio_tungstenite::tungstenite::Error as TungsteniteError;

pub type Program = hypershell! {
        WebSocket<
            StaticArg<"wss://jetstream1.us-west.bsky.network/subscribe">,
            (),
        >
    |   StreamingExec<
            StaticArg<"grep">,
            WithArgs [ FieldArg<"keyword"> ],
        >
    |   StreamToStdout
};

#[derive(HasField)]
pub struct MyApp {
    pub keyword: String,
}

delegate_components! {
    MyApp {
        namespace HypershellNamespace;

        @cgp.core.error.ErrorRaiserComponent.TungsteniteError:
            RaiseAnyhowError,

        @cgp.extra.handler.HandlerComponent.<Url, Params> WebSocket<Url, Params>:
            HypershellTungsteniteProvider,
    }
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    let app = MyApp {
        keyword: "love".to_owned(),
    };

    let (read, _write) = simplex(102400);
    let input = TokioAsyncReadStream::from(read);

    app.handle(PhantomData::<Program>, input).await?;

    Ok(())
}
```

## Context and wiring

The namespace routes neither `WebSocket` nor `tungstenite::Error`, so the context adds both as
entries beside its `namespace` statement, using the full prefixed paths. The entry for the error
names `ErrorRaiserComponent` as a path segment, so the component must be imported even though the
code never mentions it otherwise.

The input is a Tokio reader over a pipe whose writer is kept alive and never written. The WebSocket
handler forwards its input to the socket and closes the socket when the input ends, so an empty
`Vec<u8>` would end the stream immediately. The second parameter of `WebSocket` is `()`; the handler
ignores it.

## Try a change

Removing the error route while keeping the `WebSocket` entry is the change the public page shows. A
probe checked the program with
`HandlerComponent: (Program, TokioAsyncReadStream<ReadHalf<SimplexStream>>)`, the input `main`
builds, and `cargo cgp check` built from source at commit `b6a6323` reported:

```text
error[E0277]: [CGP-E002] the provider trait `Handler<Pipe<…>, TokioAsyncReadStream<ReadHalf<SimplexStream>>>` with context `MyApp` is not implemented for provider `ComposeHandlers<…>`
   = note: root cause: [CGP-E107] context `MyApp` does not contain any delegate entry for `@cgp.core.error.ErrorRaiserComponent.Error`
```

The path's last segment is `tungstenite::Error` written by its own name, `Error`, so the message
names the error type the provider raises rather than the context's `anyhow` error. With the route in
place, the check passes.

## What it demonstrates

- Adding a syntax and an error type on one context: see
  [assembly](../architecture/assembly.md#layer-three-contexts) and
  [error handling](../architecture/error-handling.md#every-source-error-type-is-listed-twice).
- Per-input dispatch under one syntax: see
  [streams and input dispatch](../architecture/streams-and-input-dispatch.md#dispatching-on-the-input-type).
- The WebSocket extension: see
  [extensions](../reference/extensions.md#websocket-and-handlewebsocket).

## Public material derived from this

The `examples/bluesky-websocket` page of the
[Hypershell project section](../../../website/projects/hypershell.md).
