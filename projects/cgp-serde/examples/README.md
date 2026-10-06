# cgp-serde examples

This directory documents each example in the repository's `cgp-serde-examples` crate: what the
example does, the data types and context it defines, what running it produces, and which parts of
the architecture and reference it demonstrates. The crate holds the four examples as Cargo example
targets under `examples/`, and has no library code of its own. Each example defines its own data
types and contexts, and together they cover a JSON round trip, the two-application demo, and arena
deserialization in two forms. The provider suites in `cgp-serde-tests` are tests rather than
examples; [testing.md](../testing.md#the-provider-suites) records them.

## How these differ from the top-level example

**These documents are records of the repository's examples; the top-level [modular serialization
example](../../../examples/modular-serialization.md) is the teaching progression to quote.** That
example develops the scenario step by step for an agent writing a tutorial or a page, and imports
the cgp-serde crates to do it. The documents here each describe one example as the repository ships
it, including its dead wiring and redundant checks, so an agent quoting an example knows what it is
quoting. Where the two overlap, as for the two applications and the arena, the top-level example
owns the explanation and a document here links to it.

**Each document quotes the snippets that carry the example's ideas, not the whole file.** The
**Source** link in its header leads to the full example. A snippet may join an entry the source
spreads over several lines, or elide unrelated entries as `// ...`, but it never changes what the
code says, so a snippet still compiles once the elided entries are restored.

## The shape they wire

**Every example wires an environmental context, and every serialization component in them is
parameter-targeted.** The wired types, `App`, `AppA`, `AppB`, and `App<'a>`, stand for applications
rather than for the data being encoded, and the value being serialized is the component's `Value`
parameter. That is the fully modular shape the [modularity
hierarchy](../../../cgp/concepts/modularity-hierarchy.md) places on tier 4, chosen because the
encoded types, such as `Vec<u8>` and `DateTime<Utc>`, are foreign and different applications must
encode them differently; see [component design](../architecture/component-design.md). `App`, `AppA`,
and `AppB` are fieldless, which is complete rather than a placeholder. The two arena examples'
`App<'a>` carries one field, the arena, because a provider draws it from the context during
deserialization.

## Running an example

Each example runs from the repository root with `cargo run -p cgp-serde-examples --example <name>`,
which prints its result. Each example also carries its assertions as a `#[test]` function, and its
Cargo target sets `test = true`, so `cargo test -p cgp-serde-examples` runs all four and
`cargo test -p cgp-serde-examples --example <name>` runs one. The workspace pins Rust 1.98.1 in
`rust-toolchain.toml` and overrides `cgp` and `cgp-error-anyhow` with the `cgp` repository's `main`
branch through `[patch.crates-io]`, which the first build fetches; see [crate
layout](../architecture/crate-layout.md#build-facts). Once built, no example needs a network or any
program outside the build. The table records what each did when run against the `v0.8.0` branch:

| Example | Prints | Its test |
|---|---|---|
| [`basic`](basic.md) | the JSON and the value read back | passes; asserts both |
| [`messages`](messages.md) | both applications' JSON | passes; asserts both documents |
| [`arena_simplified`](arena-simplified.md) | the deserialized value | passes; asserts it |
| [`arena`](arena.md) | the deserialized value | passes; asserts it |

`cargo test --workspace` runs all four tests, and each example compiles with no warnings.

## The catalog

The order is the order the examples teach in, from one round trip to a deserializer that draws a
service from its context.

- [basic.md](basic.md): one struct serialized to JSON and read back, through the JSON `TryComputer`
  providers, with its bytes as hex.
- [messages.md](messages.md): the two-application demo: nested data encoded as hex and RFC 3339 by
  one context, and as base64 and Unix timestamps by another.
- [arena-simplified.md](arena-simplified.md): borrowed values deserialized into an arena the context
  supplies, with a getter and deserializer local to the example, as in the announcement post.
- [arena.md](arena.md): the same through the layered allocation crates, where the allocator is a
  wiring choice.

## What the examples leave out

The four examples exercise most of the library's providers but not all of them, so they are not a
tour of every provider. None of them runs the byte providers, `SerializeWithDisplay`,
`DeserializeWithFromStr`, `SerializeFrom`, `TrySerializeFrom`, or `DeserializeDefault`, none uses a
format other than JSON, and none feeds invalid input. [testing.md](../testing.md) records the
coverage in full, including the provider suites, and the [reference](../reference/README.md)
documents the rest of the providers from probes.

## Public material derived from this

The `examples/index` page of the
[cgp-serde project section](../../../website/projects/cgp-serde.md), and an examples section of the
repository README.
