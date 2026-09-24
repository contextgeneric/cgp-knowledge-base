# Crate layout

cgp-serde is split into five library crates so that each external dependency lives in its own crate,
and an application compiles only the dependencies its wiring actually names. This document records the
crates, what depends on what, and why the allocation support is two crates rather than one.

## The dependency graph

**Every library crate depends on `cgp`, and every crate but the core depends on the core.** The core
crate, `cgp-serde`, depends only on `cgp` and `serde`. Each of the others adds the external
dependencies of its own providers and nothing else:

| Crate | Depends on, beyond `cgp` and `serde` | Holds |
|---|---|---|
| `cgp-serde` | nothing | the two components, the two context adapters, the core providers |
| `cgp-serde-extra` | `cgp-serde`, `hex`, `base64`, `chrono` | the hex, base64, RFC 3339, and timestamp encodings |
| `cgp-serde-json` | `cgp-serde`, `serde_json` | the JSON codes, providers, and convenience method |
| `cgp-serde-alloc` | `cgp-serde` | the `CanAlloc` component and `DeserializeAndAllocate` |
| `cgp-serde-typed-arena` | `cgp-serde`, `cgp-serde-alloc`, `typed-arena` | the arena getter and `AllocateWithArena` |

The test crate, `cgp-serde-tests`, depends on all five, on `cgp-error-anyhow` for a concrete error type,
and on Serde's `derive` feature. No library crate depends on `cgp-error-anyhow`: the JSON providers
name only `HasErrorType` and `CanRaiseError`, and the application chooses the error type.

The graph is the practical form of the design's main promise. A crate that defines data types needs
only `cgp`, to derive the field traits the record providers read, and depends on neither `serde` nor
any cgp-serde crate; see [derive-free records](derive-free-records.md). An application depends on the
cgp-serde crates whose providers it wires, so choosing hex over base64 is also choosing to compile
`hex` and not `base64`.

## Why allocation is two crates

**The allocation component and its arena implementation are separate crates so that the allocator is
a wiring choice rather than a dependency of the deserializer.** `cgp-serde-alloc` defines what
allocation means, `CanAlloc<'a, T>`, and the provider that deserializes a borrowed value through it,
and it adds no external dependency. `cgp-serde-typed-arena` is one implementation of `CanAlloc`, over
`typed-arena`. An application using a different allocator would implement the component itself and
depend on `cgp-serde-alloc` alone. The layering is described in
[context services](context-services.md).

## Module layout

Every crate uses the same small set of module names, so a reader can find the kind of item they want
by its module:

- **`components`** — CGP components defined by the crate (`cgp-serde` only).
- **`traits`** — components and getters that support a provider rather than being serialization
  components themselves (`cgp-serde-alloc`, `cgp-serde-typed-arena`).
- **`providers`** — provider structs, one file per family.
- **`types`** — public non-provider types, the two context adapters (`cgp-serde` only).
- **`code`** — `Code` types that key handler wiring (`cgp-serde-json` only).
- **`impls`** — blanket traits built with `#[cgp_fn]` (`cgp-serde-json` only).

Each module re-exports its files with `pub use`, so an item is imported from the module rather than
the file, as in `cgp_serde::providers::SerializeFields`.

## Build facts

Every library crate declares `#![no_std]`. All but `cgp-serde-alloc` and `cgp-serde-typed-arena` also
link `alloc`, for `String` and `Vec`. The workspace uses edition 2024 with a minimum Rust version of
1.90, pins its development toolchain to Rust 1.98.1 in `rust-toolchain.toml`, and depends on `cgp`
0.8.0-alpha. All five crates carry version 0.2.0.

## Source

- [`Cargo.toml`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/Cargo.toml) — the workspace
  members and shared dependencies.
- [`crates/`](https://github.com/contextgeneric/cgp-serde/tree/v0.8.0/crates) — one directory per crate,
  each with its own `Cargo.toml`.

## Public material derived from this

The installation and crate list of the repository README.
