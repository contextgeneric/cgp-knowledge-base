# `http_checksum_native`

The checksum pipeline with both commands replaced by the checksum extension, run on a context that
joins an extension namespace instead of the base one.

- **Source**: [crates/hypershell-examples/examples/http_checksum_native.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/http_checksum_native.rs)
- **Run**: `cargo run --example http_checksum_native`
- **Needs**: network
- **Result**: prints the same digest as `http_checksum_cli`

## The program

```rust
use hypershell::prelude::*;
use hypershell_examples::namespaces::HypershellChecksumNamespace;
use hypershell_hash_components::dsl::{BytesToHex, Checksum};
use reqwest::Client;
use sha2::Sha256;

pub type Program = hypershell! {
    StreamingHttpRequest<
        GetMethod,
        FieldArg<"url">,
        WithHeaders[ ],
    >
    | Checksum<Sha256>
    | BytesToHex
    | StreamToStdout
};

#[derive(HasField)]
pub struct MyApp {
    pub http_client: Client,
    pub url: String,
}

delegate_components! {
    MyApp {
        namespace HypershellChecksumNamespace;
    }
}
```

## Context and wiring

The only change from `http_checksum_client` besides the program is the namespace:
`HypershellChecksumNamespace` inherits `HypershellNamespace` and routes `Checksum` and `BytesToHex` to
the examples crate's `HypershellChecksumProvider`; see [the examples library](README.md#the-examples-library).
`Checksum<Sha256>` names the algorithm type directly, so the program depends on `sha2`. The digest
is raw bytes, which `BytesToHex` encodes for printing.

## Try a change

Removing the `BytesToHex` stage is the change the public page shows. The raw `GenericArray` digest then
reaches `StreamToStdout`, whose input dispatcher has no entry for it. A probe checked the program on
the same context with `HandlerComponent: (Program, Vec<u8>)`, and `cargo cgp check` built from source
at commit `b6a6323` reported:

```text
error[E0277]: [CGP-E002] the provider trait `Handler<Pipe<…>, GenericArray<u8, …>>` with context `MyApp` is not implemented for provider `Call<StreamToStdout>`
   = note: root cause: [CGP-E110] provider `HandleToTokioAsyncRead` does not contain any delegate entry for `@HandlerComponent.StreamToStdout.GenericArray<u8, …>`
```

The published `cargo-cgp` v0.1.0-alpha reports the same leaf as `[CGP-E107]`, calling
`HandleToTokioAsyncRead` a context; the dedicated `[CGP-E110]` code is newer than that release. See
[debugging](../guides/debugging.md#a-stage-cannot-accept-the-previous-stages-output).

## What it demonstrates

- A language extension joined by changing one namespace name: see
  [extending the language](../guides/extending-the-language.md).
- The checksum extension: see [extensions](../reference/extensions.md).
- The same scenario as the top-level [shell-scripting DSL example](../../../examples/shell-scripting-dsl.md),
  which owns the teaching version.

## Known issues

The file sets `#![recursion_limit = "256"]`, which the
pinned toolchain does not need. See [issues.md](../issues.md#housekeeping).

## Public material derived from this

The `examples/http-checksum-native` page of the planned [Hypershell project
section](../../../website/projects/hypershell.md).
