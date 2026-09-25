# `http_checksum_cli`

The shell pipeline `curl $url | sha256sum | cut -d ' ' -f 1`, written as three streaming stages
that run concurrently.

- **Source** — [crates/hypershell-examples/examples/http_checksum_cli.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/http_checksum_cli.rs)
- **Run** — `cargo run --example http_checksum_cli`
- **Needs** — network, `curl`, `sha256sum`, `cut`
- **Result** — prints the SHA-256 digest of the Nixpkgs manual page, the same digest as
  `http_checksum_client` and `http_checksum_native`

## The program

```rust
pub type Program = hypershell! {
    StreamingExec<
        StaticArg<"curl">,
        WithArgs [
            FieldArg<"url">,
        ],
    >
    |   StreamingExec<
            StaticArg<"sha256sum">,
            WithStaticArgs [],
        >
    |   StreamingExec<
            StaticArg<"cut">,
            WithStaticArgs [
                "-d",
                " ",
                "-f",
                "1",
            ],
        >
    | StreamToStdout
};

#[derive(HasField)]
pub struct MyApp {
    pub url: String,
}

delegate_components! {
    MyApp {
        namespace HypershellNamespace;
    }
}
```

`main` constructs `MyApp` with `url: "https://nixos.org/manual/nixpkgs/unstable/"` and calls
`handle` with `Vec::new()`.

## Context and wiring

Each `StreamingExec` spawns its process and returns its standard output as a stream at once, with its
input copied into standard input on a Tokio task, so the three processes run in parallel as in a
shell. Each stage's output is a `TokioAsyncReadStream`, which the next stage's input dispatcher
accepts. `WithStaticArgs []` expands to an empty argument list.

## What it demonstrates

- Streaming execution and concurrent stages: see [execution](../reference/execution.md#streamingexec-and-handlestreamingexec).
- Stage types lining up through the input dispatcher: see
  [streams and input dispatch](../architecture/streams-and-input-dispatch.md).

## Known issues

The streaming stages ignore exit status and standard error, so a failing `curl` produces the digest
of whatever it wrote, possibly nothing, rather than an error; see
[issues.md](../issues.md#streamingexec-ignores-the-exit-status-and-standard-error).

## Public material derived from this

The streaming program in the planned [Hypershell deep dive](../../../website/deep-dives/hypershell.md).
