# cgp-serde

`cgp-serde` rebuilds [Serde](https://serde.rs/)'s `Serialize` and `Deserialize` as CGP components, so
that how each value type is encoded stops being a fixed property of the type and becomes a per-context
wiring choice. Overlapping and orphan serialization implementations become legal, and a deserializer
can draw services such as an arena allocator from the context it runs in.

- **Repository** — <https://github.com/contextgeneric/cgp-serde>
- **Local checkout** — `../cgp-serde`, per [sibling-projects.md](../../sibling-projects.md)
- **Branch documented** — `v0.8.0`
- **Crates** — `cgp-serde`, `cgp-serde-extra`, `cgp-serde-json`, `cgp-serde-alloc`,
  `cgp-serde-typed-arena`, all at 0.2.0
- **Tracks** — `cgp` 0.8.0-alpha
- **Status** — Proof of concept; see [Status and gaps](#status-and-gaps)

## What it is

The library defines two components that mirror Serde's traits with one structural change.
`CanSerializeValue<Value>` and `CanDeserializeValue<'de, Value>` move the type being encoded out of
`Self` into an explicit `Value` parameter, leaving `Self` to be a **context** that carries the wiring.
That move does two things at once. The implementing type of each provider is now a struct the library
owns, so implementations that would overlap as blanket `Serialize` impls can coexist: `UseSerde` for
anything that already implements `Serialize`, `SerializeBytes` for anything `AsRef<[u8]>`, and
`SerializeWithDisplay` for anything `Display`. And every method now takes `&self`, so a provider can
reach into the context: to ask how a nested value should be encoded, or to fetch a runtime service.

Two results follow that plain Serde cannot deliver. Two applications can wire different providers for
`Vec<u8>` and `DateTime<Utc>` and produce different JSON from the same value, differing only in a few
wiring lines. And a data type needs **no serialization-specific derive**: deriving CGP's
general-purpose field traits is enough for the generic record providers, so a library can expose
serializable types without depending on `serde` or `cgp-serde` at all.

cgp-serde replaces only Serde's `Serialize`/`Deserialize` layer. Serde's data model and its
`Serializer` and `Deserializer` traits are used unchanged, and adapter types carry a context-aware value
into any API that expects an ordinary `Serialize` or `DeserializeSeed`. Self-describing formats such
as JSON and RON work with it; length-prefixed binary formats such as postcard do not yet, because the
record and sequence providers do not declare a length. The design is set out in
[architecture/](architecture/README.md).

## Which revision these documents describe

These documents describe the `v0.8.0` branch, which tracks `cgp` 0.8.0-alpha and is not yet released.
The crates on crates.io and the repository's `main` branch are the 0.2.0 release, built against `cgp`
0.7.0; the `v0.8.0` branch still carries version 0.2.0 in its manifests. The library crates on the two
branches offer the same components and providers and differ only in attribute syntax that `cgp`
0.8.0-alpha changed, while the tests on `v0.8.0` wire per-type dispatch with the `open` statement
where the release builds `UseDelegate` tables. So what these documents say a provider does holds for
both, but code quoted from them compiles only against the `v0.8.0` branch. Source links point at that branch, per
[../AGENTS.md](../AGENTS.md#a-project-section-documents-its-project-in-depth).

## How it is organized

The workspace holds five library crates and a test crate. The split follows external dependencies,
so an application depends only on the crates whose providers its wiring names. Every library crate is
`no_std` with `alloc`.

- **`cgp-serde`** — the two components, the two context adapters, and the core providers. Depends only
  on `cgp` and `serde`.
- **`cgp-serde-extra`** — the hex, base64, RFC 3339, and Unix-timestamp encodings, over `hex`, `base64`,
  and `chrono`.
- **`cgp-serde-json`** — `serde_json` providers built on CGP's `TryComputer` handler, and a
  `deserialize_json_string` convenience method.
- **`cgp-serde-alloc`** — an allocation component and the provider that deserializes a borrowed value
  into it. Adds no external dependency.
- **`cgp-serde-typed-arena`** — an implementation of the allocation component over `typed-arena`.
- **`cgp-serde-tests`** — the test crate: a JSON round trip, the two-application serialization demo,
  and the arena deserialization demo in its layered and simplified forms.

## Status and gaps

The library handles named-field structs, the common scalar and collection types, and any type that
already implements Serde's traits, but it is a proof of concept with gaps that have each been
confirmed against the `v0.8.0` branch:

- **Enums** — no provider serializes an enum generically; an enum works only through `UseSerde`, from
  its own `Serialize` or `Deserialize` impl.
- **Recursive data types** — a type that contains itself, such as a tree node with a `Vec` of children,
  fails to compile through the generic providers and needs a provider written for it; see
  [re-entrant providers](architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).
- **Tuple structs** — the record providers accept only named fields.
- **Binary formats** — length-prefixed formats such as postcard reject records and sequences, because
  the providers do not declare a length.
- **Serde's attributes** — fields cannot be renamed, skipped, flattened, or defaulted when missing.
- **JSON helpers** — the JSON providers deserialize from any `serde_json` reader, but the only
  convenience method takes a string; there is no counterpart for serializing.
- **Evidence** — no benchmark has been run, the source has no rustdoc, and the tests assert little:
  the two-application demo prints its output without checking it.

## The documents

The section follows the project shape in [../AGENTS.md](../AGENTS.md#the-shape-of-a-project-section).
Start with the architecture for the ideas every provider shares, then use the reference to look up a
provider.

- [architecture/](architecture/README.md) — the design on one page, and one document per idea:
  - [reentrant-providers.md](architecture/reentrant-providers.md) — how a provider hands each nested
    value back to the context through the two adapter types, which is what makes wiring reach
    arbitrarily deep.
- [reference/](reference/README.md) — every public item, grouped by family, with a table of all
  providers:
  - [records.md](reference/records.md) — `SerializeFields` and `DeserializeRecordFields`, the
    derive-free struct providers.

## Public material derived from these documents

These documents are the source for the project's public writing, and each one names what it feeds.
Three artifacts are planned:

- **The cgp-serde deep dive** on the website, specified in
  [website/deep-dives/cgp-serde.md](../../website/deep-dives/cgp-serde.md). Its five pages draw on the
  architecture for the component design, the reference and guides for providers and wiring, and the
  comparison and issues documents for the page on what the library does not do.
- **The repository README**, which currently summarizes the components in pre-0.8 syntax and defers to
  the announcement post.
- **Rustdoc for every public item.** The source carries no doc comments, so the crates' docs.rs pages
  list items without explanation; the reference entries are written to be condensed into them.

## How it relates to the rest of the base

The [modular serialization example](../../examples/modular-serialization.md) develops the project's
scenario end to end. The [announcement post](../../website/blog/cgp-serde-release.md) is the fullest
published account, written against an earlier release; its document records what has drifted. The
project was also the live demonstration in the
[RustLab 2025 talk](../../website/blog/rustlab-2025-coherence.md).

On the CGP side, the library is the clearest available demonstration of
[bypassing coherence](../../cgp/concepts/coherence.md), whose worked illustration uses cgp-serde's own
providers. Its per-type wiring uses the `open` statement of
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md), its record providers rest
on [extensible records](../../cgp/concepts/extensible-records.md) and the
[optional builder](../../cgp/reference/traits/optional_fields.md), its JSON helpers raise errors
through [modular error handling](../../cgp/concepts/modular-error-handling.md), and its
lifetime-carrying deserialization component is checked with [`Life`](../../cgp/reference/types/life.md)
in [`check_components!`](../../cgp/reference/macros/check_components.md).

Two related-work documents use the library as their CGP example.
[Reflection](../../related-work/reflection.md) compares the record providers with Serde's derive and
with runtime and compile-time reflection, and
[Rust language proposals](../../related-work/rust-language-proposals.md) reads the arena deserializer
as a library-level form of the context-and-capabilities proposal.

For the communication strategy this is the ecosystem's strongest argument, because Serde is
universally known and the orphan-rule pain around it is widely felt; the framing belongs in
[message.md](../../communication-strategy/message.md#the-problems-cgp-removes).
