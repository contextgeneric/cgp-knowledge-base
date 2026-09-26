# `parallel_compare`

Two checksum sub-pipelines run concurrently and compared with the examples library's `Compare`
syntax, with the sub-pipeline written once as a generic type alias.

- **Source** — [crates/hypershell-examples/examples/parallel_compare.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/parallel_compare.rs)
- **Run** — `cargo run --example parallel_compare`
- **Needs** — network
- **Result** — prints `equals: true`.

## The program

```rust
pub type GetChecksumOf<Url> = hypershell! {
    StreamingHttpRequest<
        GetMethod,
        Url,
        WithHeaders[ ],
    >
    | Checksum<Sha256>
    | BytesToHex
};

pub type Program = hypershell! {
    Compare<
        GetChecksumOf<FieldArg<"url_a">>,
        GetChecksumOf<FieldArg<"url_b">>,
    >
};

#[derive(HasField)]
pub struct MyApp {
    pub http_client: Client,
    pub url_a: String,
    pub url_b: String,
}

delegate_components! {
    MyApp {
        namespace HypershellCompareNamespace;
    }
}
```

`main` sets `url_a` to the Nixpkgs manual's URL with a trailing slash and `url_b` to the same URL
without one, and passes `(Vec::new(), Vec::new())`, one input per compared program.

## Context and wiring

`GetChecksumOf<Url>` is an ordinary generic type alias over a program, so a sub-pipeline is written
once and instantiated per URL. `HypershellCompareNamespace` adds `Compare` and `If` on top of the
checksum namespace, and wires `Compare` through `BoxHandler`; see
[the examples library](README.md#the-examples-library).

The example demonstrates that the two URLs serve the same page. The URL without the slash answers
301, and the streaming request follows it because its `Vec<u8>` input is sent as a buffered body; see
[HTTP](../reference/http.md#streaminghttprequest-and-handlestreaminghttprequest).

## What it demonstrates

- Control syntax whose operands are whole programs: see
  [extending the language](../guides/extending-the-language.md#add-control-syntax).
- Generic program aliases, and `|` inside a type argument: see [the macro reference](../reference/macro.md).

## Known issues

The file sets `#![recursion_limit = "512"]`, which the pinned toolchain does not need. On stable Rust
without the new trait solver, checking this example grew `rustc` to about 7 GB before it was killed;
see [crate layout](../architecture/crate-layout.md#build-facts).

## Public material derived from this

None yet.
