# `bluesky`

A long-running stream: the Bluesky firehose read by `websocat`, provisioned on the fly by
`nix-shell`, and filtered by `grep` for a keyword from the context.

- **Source** — [crates/hypershell-examples/examples/bluesky.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/bluesky.rs)
- **Run** — `cargo run --example bluesky`, stopped with Ctrl-C
- **Needs** — network, `nix-shell` (which fetches `websocat` on first use), `grep`
- **Result** — streams firehose events containing `love` until stopped; about 45 KB in two minutes
  when probed

## The program

```rust
pub type Program = hypershell! {
        StreamingExec<
            StaticArg<"nix-shell">,
            WithStaticArgs [
                "-p",
                "websocat",
                "--run",
                "websocat -nU wss://jetstream1.us-west.bsky.network/subscribe",
            ],
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
```

The context joins `HypershellNamespace`, and `main` sets `keyword: "love"`.

## Context and wiring

Both stages are `StreamingExec`, so the program never ends on its own: output flows as the firehose
produces it. The first stage passes a whole shell command line as one literal argument to
`nix-shell --run`.

## What it demonstrates

- A pipeline that streams indefinitely: see [streams and input dispatch](../architecture/streams-and-input-dispatch.md#how-a-streaming-stage-runs).
- The contrast with [`bluesky_websocket`](bluesky-websocket.md), which replaces the external tool with
  the WebSocket extension.

## Known issues

The file sets `#![recursion_limit = "256"]`, which the pinned toolchain does not need. See
[issues.md](../issues.md#housekeeping).

## Public material derived from this

None yet.
