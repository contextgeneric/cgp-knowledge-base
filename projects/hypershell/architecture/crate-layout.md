# Crate layout

Hypershell is split so that each backend library lives in its own crate, and a crate compiles only
the backends it interprets. This document records the nine crates, what depends on what, the shared
module layout, and the toolchain the workspace needs.

## The dependency graph

**The syntax and the component interfaces live in `hypershell-components`, which depends only on
`cgp`, and each backend crate adds one external library.** The concrete contexts and the namespace
are assembled last, in `hypershell`. The workspace's crates are:

| Crate | Depends on, beyond `cgp` | Holds |
|---|---|---|
| `hypershell-components` | nothing | the syntax types, the extractor components, the control providers, `HypershellBaseProvider` |
| `hypershell-tokio-components` | `hypershell-components`, `tokio`, `tokio-util`, `futures`, `itertools` | processes, files, streams and their wrappers, `CommandUpdater`, `HypershellTokioProvider` |
| `hypershell-reqwest-components` | `hypershell-components`, `hypershell-tokio-components`, `reqwest`, `url`, `tokio`, `tokio-util`, `futures` | HTTP, the request-builder updater, the client getter, `HypershellReqwestProvider` |
| `hypershell-json-components` | `hypershell-components`, `serde`, `serde_json` | `HandleEncodeJson`, `HandleDecodeJson`, `HypershellJsonProvider` |
| `hypershell-hash-components` | `sha2`, `hex`, `futures` | the `Checksum` and `BytesToHex` syntax and their providers |
| `hypershell-tungstenite-components` | `hypershell-components`, `hypershell-tokio-components`, `tokio-tungstenite`, `tokio`, `tokio-util`, `futures` | `HandleWebsocket` and `HypershellTungsteniteProvider` |
| `hypershell-macro` | `proc-macro2`, `quote` | the `hypershell!` macro |
| `hypershell` | the components, Tokio, reqwest, JSON, and macro crates, `cgp-error-anyhow`, `reqwest`, `url`, `serde_json` | `HypershellNamespace`, `HypershellErrorHandler`, `HypershellCli`, `HypershellHttp`, the prelude |
| `hypershell-examples` | `hypershell`, the components, Tokio, and hash crates, and the libraries the examples use | the `Compare` and `If` extension, the checksum and compare namespaces, the runnable examples and the tests |

The graph is the practical form of the claim that CGP inverts dependencies. Because providers are
written against an abstract context and concrete types are named only in `hypershell`, the Tokio
crate builds without `reqwest` in its tree, and the JSON crate builds without Tokio. Two edges are
worth knowing, because the announcement post describes the graph as flatter than it is:

- **The reqwest and tungstenite crates depend on the Tokio crate**, for the stream wrapper types and
  the input dispatchers their wiring composes. An HTTP backend without Tokio would need its own
  adapters, not only its own client.
- **`hypershell-hash-components` depends on neither `hypershell-components` nor Tokio.** Its
  syntax and providers name only CGP's `Handler`, so the crate could serve any DSL built on the
  handler family. It ships no bundle; the one in `hypershell-examples` wires it together with the
  Tokio crate's `HandleToFuturesStream`.

**The `hypershell` crate does not include the extensions.** Neither the hash nor the tungstenite
crate is a dependency of `hypershell`, and `HypershellNamespace` routes neither `Checksum` nor
`WebSocket`. A program using them needs an extension namespace or context entries, as the examples
show; see [extending the language](../guides/extending-the-language.md).

## Module layout

The library crates share a small set of module names, so a reader can find the kind of item they want
by its module:

- **`dsl`** — syntax types (`hypershell-components`, and the core or extension syntax of the Tokio,
  reqwest, and hash crates).
- **`components`** — CGP components defined by the crate.
- **`providers`** — provider structs, one file per family, with the crate's bundle in `combined.rs`.
- **`types`** — the stream wrapper types (`hypershell-tokio-components` only).
- **`traits`** — `WrapCall` and `WrapStaticArg`, type-level list maps (`hypershell-components` only).

The assembly crate uses `contexts`, `namespaces`, `providers` (for the error aggregate), and
`prelude`. Each module re-exports its files with `pub use`, so an item is imported from the module,
as in `hypershell_tokio_components::providers::HandleSimpleExec`.

**`hypershell::prelude` is what a program file imports.** It re-exports `cgp::prelude::*`,
`PhantomData`, `CanHandle`, the anyhow `Error`, every syntax type in `hypershell_components::dsl`,
the `hypershell!` macro, and the two contexts. It does not re-export `HypershellNamespace`, which a
custom context imports from `hypershell::namespaces`, nor the Tokio crate's `ToTokioAsyncRead`
adapter syntax. The macro depends on the prelude being in scope; see [the macro reference](../reference/macro.md).

## Build facts

`hypershell-components` and `hypershell-json-components` declare `#![no_std]` and link `alloc`. The
other crates use `std`. The workspace uses edition 2024 and declares a minimum Rust version of 1.90.

**The workspace pins the nightly toolchain and enables the next-generation trait solver.** Its
`rust-toolchain.toml` selects `nightly`, and `.cargo/config.toml` passes `-Z next-solver=globally`.
Probes show the setting matters for the largest programs. On stable Rust 1.98.1 without the new
solver, the library crates and most examples check, but `parallel_compare` and `compare_and_branch`
grew `rustc` to about 7 GB and were killed after roughly 90 seconds on an 11 GB machine. With nightly
and the new solver, a fresh check of `parallel_compare` took about 9 seconds and 460 MB. In a
full-workspace stable check `http_checksum_native` also failed, but it passed when checked alone,
which points to memory pressure from the concurrent compare examples rather than a type error. The
cause of the difference was not investigated further.

Several example files and the test crate set `#![recursion_limit = "256"]` or `"512"`. Under the
pinned toolchain they are not needed: the examples check and build without them.

**The workspace builds only beside a local `cgp` checkout.** The root `Cargo.toml` patches `cgp` and
`cgp-error-anyhow` to paths under `../cgp`, so a fresh clone of Hypershell alone does not build. The
patch and the stale `repository` field are recorded in [issues.md](../issues.md#housekeeping).

## Source

- The workspace manifest: [Cargo.toml](https://github.com/contextgeneric/hypershell/blob/v0.8.0/Cargo.toml)
- The toolchain: [rust-toolchain.toml](https://github.com/contextgeneric/hypershell/blob/v0.8.0/rust-toolchain.toml) and [.cargo/config.toml](https://github.com/contextgeneric/hypershell/blob/v0.8.0/.cargo/config.toml)
- The prelude: [crates/hypershell/src/prelude.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/prelude.rs)

## Public material derived from this

The crate-structure argument on page 2 of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md), and the crate list in the
repository README.
