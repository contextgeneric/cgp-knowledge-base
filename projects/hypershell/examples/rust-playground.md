# `rust_playground`

A Rust value encoded to JSON, posted to the Rust Playground's gist API, and the JSON response decoded
back into a Rust type, on the predefined `HypershellHttp` context.

- **Source** — [crates/hypershell-examples/examples/rust_playground.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/rust_playground.rs)
- **Run** — `cargo run --example rust_playground`
- **Needs** — network
- **Result** — not run while documenting, because running it publishes a public GitHub gist of the
  snippet. It compiles against the `v0.8.0` branch.

## The program

```rust
pub type Program = hypershell! {
    EncodeJson
    |   SimpleHttpRequest<
            PostMethod,
            StaticArg<"https://play.rust-lang.org/meta/gist">,
            WithHeaders [
                Header<
                    StaticArg<"Content-Type">,
                    StaticArg<"application/json">,
                >
            ],
        >
    |   DecodeJson<Response>
};

#[derive(Serialize)]
pub struct Request {
    pub code: String,
}

#[derive(Debug, Deserialize)]
pub struct Response {
    pub id: String,
    pub url: String,
    pub code: String,
}
```

`main` runs the program on `HypershellHttp { http_client: Client::new() }` with a `Request` as the
input.

## Context and wiring

The program starts with `EncodeJson`, so its input is a Rust value rather than bytes, and it ends
with `DecodeJson<Response>`, so its output is a `Response`. The JSON bytes from `EncodeJson` are the
POST body directly, since `SimpleHttpRequest` takes any `Into<reqwest::Body>`. `HypershellHttp` is
enough because the program reads no field other than the client.

## What it demonstrates

- A program whose input and output are Rust types: see [interpretation](../architecture/interpretation.md#handler-is-the-interpreter-interface).
- `HypershellHttp`: see [contexts and namespace](../reference/contexts-and-namespace.md#hypershellhttp).
- JSON in both directions: see [JSON](../reference/json.md).

## Public material derived from this

The JSON program in the planned [Hypershell deep dive](../../../website/deep-dives/hypershell.md).
