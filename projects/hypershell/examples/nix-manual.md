# `nix_manual`

A native HTTP request feeding two external commands, with a static URL and an argument list that
mixes a literal with a field.

- **Source** — [crates/hypershell-examples/examples/nix_manual.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/nix_manual.rs)
- **Run** — `cargo run --example nix_manual`
- **Needs** — network, `tr`, `grep`
- **Result** — prints the lines of the Nixpkgs manual containing `Nix`, in upper case

## The program

```rust
pub type Program = hypershell! {
    StreamingHttpRequest<
            GetMethod,
            StaticArg<"https://nixos.org/manual/nixpkgs/unstable/">,
            WithHeaders<Nil>,
        >
    |   StreamingExec<
            StaticArg<"tr">,
            WithStaticArgs [
                "[:lower:]",
                "[:upper:]",
            ],
        >
    |   StreamingExec<
            StaticArg<"grep">,
            WithArgs [
                StaticArg<"-i">,
                FieldArg<"keyword">,
            ],
        >
    | StreamToStdout
};

#[derive(HasField)]
pub struct MyApp {
    pub http_client: Client,
    pub keyword: String,
}
```

The context joins `HypershellNamespace`, and `main` sets `keyword: "Nix"`.

## Context and wiring

The URL is a `StaticArg`, parsed as a `url::Url` by the URL extractor. The headers are written as
`WithHeaders<Nil>`, which is exactly what `WithHeaders[]` expands to. The `grep` arguments mix a
literal and a field in one `WithArgs` list.

## What it demonstrates

- A static URL through the layered URL extractor: see [arguments](../reference/arguments.md#extractstringcommandarg-extractstringurlarg-and-extracturlfieldarg).
- Writing the expanded form by hand next to the sugared form: see [the macro reference](../reference/macro.md).

## Public material derived from this

None yet.
