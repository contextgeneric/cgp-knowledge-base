# `save_webpage`

A streaming HTTP request written straight to a file whose path comes from a context field.

- **Source** — [crates/hypershell-examples/examples/save_webpage.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/save_webpage.rs)
- **Run** — `cargo run --example save_webpage`, from a directory where it may write
- **Needs** — network
- **Result** — writes the Nixpkgs manual to `nix_manual.html` in the working directory and prints
  `Webpage saved to nix_manual.html`

## The program

```rust
pub type Program = hypershell! {
    StreamingHttpRequest<
        GetMethod,
        FieldArg<"url">,
        WithHeaders[ ],
    >
    |   WriteFile<FieldArg<"file_path">>
};

#[derive(HasField)]
pub struct MyApp {
    pub http_client: Client,
    pub url: String,
    pub file_path: String,
}
```

The context joins `HypershellNamespace`, and `main` sets `file_path: "nix_manual.html"`, a relative
path.

## Context and wiring

`WriteFile`'s path is a command argument, so it may be a `FieldArg`, and `WriteFile` accepts the
request's futures reader through its input dispatcher. The program's output is `()`. Because the path
is relative, running the example from the repository root writes the file into the checkout.

## What it demonstrates

- `WriteFile` and its input dispatcher: see [streams and I/O](../reference/streams-and-io.md#readfile-writefile-and-their-providers).
- A path argument read from a field: see [arguments](../reference/arguments.md).

## Public material derived from this

None yet.
