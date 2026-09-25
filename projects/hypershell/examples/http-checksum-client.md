# `http_checksum_client`

The checksum pipeline with `curl` replaced by a native streaming HTTP request, mixing a native stage
with two external commands in one stream.

- **Source** — [crates/hypershell-examples/examples/http_checksum_client.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/http_checksum_client.rs)
- **Run** — `cargo run --example http_checksum_client`
- **Needs** — network, `sha256sum`, `cut`
- **Result** — prints the same digest as `http_checksum_cli`

## The program

```rust
pub type Program = hypershell! {
    StreamingHttpRequest<
        GetMethod,
        FieldArg<"url">,
        WithHeaders[ ],
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
    pub http_client: Client,
    pub url: String,
}

delegate_components! {
    MyApp {
        namespace HypershellNamespace;
    }
}
```

`main` constructs `MyApp` with `Client::new()` and the manual's URL.

## Context and wiring

The HTTP stage needs a `reqwest::Client`, which the namespace's client getter reads from a field
named exactly `http_client`. The request's output is a `FuturesAsyncReadStream`, and the next
`StreamingExec` accepts it because its input dispatcher converts a futures reader into a Tokio
reader. The program never says so; the conversion is part of `StreamingExec`'s wiring.

## What it demonstrates

- Native and external stages sharing one stream: see
  [streams and input dispatch](../architecture/streams-and-input-dispatch.md#adapters-built-into-a-syntaxs-wiring).
- The client field convention: see [HTTP](../reference/http.md#hasreqwestclient).

## Known issues

`StreamingHttpRequest` does not follow redirects. The URL here ends in a slash and does not redirect,
so the example works; the same program on the URL without the slash fails. See
[issues.md](../issues.md#streaminghttprequest-does-not-follow-redirects).

## Public material derived from this

The native-HTTP program in the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
