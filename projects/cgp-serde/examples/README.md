# cgp-serde examples

This directory documents each test in the repository's `cgp-serde-tests` crate as a worked example:
what the test does, the data types and context it defines, what running it produces, and which parts
of the architecture and reference it demonstrates. cgp-serde ships no `examples/` programs, so its four
tests are its runnable examples. Each defines its own data types and contexts, and together they cover
a JSON round trip, the two-application demo, and arena deserialization in two forms.

## How these differ from the top-level example

**These documents are records of the repository's tests; the top-level
[modular serialization example](../../../examples/modular-serialization.md) is the teaching progression
to quote.** That example develops the scenario step by step for an agent writing a tutorial or a page,
and imports the cgp-serde crates to do it. The documents here each describe one test as the repository
ships it, including its dead wiring and redundant checks, so an agent quoting a test knows what it is
quoting. Where the two overlap, as for the two applications and the arena, the top-level example owns
the explanation and a document here links to it.

**Each document quotes the snippets that carry the test's ideas, not the whole file.** The **Source**
link in its header leads to the full test. A snippet may join an entry the source spreads over several
lines, or elide unrelated entries as `// ...`, but it never changes what the code says, so a snippet
still compiles once the elided entries are restored.

## The shape they wire

**Every test wires an environmental context, and every serialization component in them is
parameter-targeted.** The wired types, `App`, `AppA`, `AppB`, and `App<'a>`, stand for applications
rather than for the data being encoded, and the value being serialized is the component's `Value`
parameter. That is the fully modular shape the
[modularity hierarchy](../../../cgp/concepts/modularity-hierarchy.md) places on tier 4, chosen because
the encoded types, such as `Vec<u8>` and `DateTime<Utc>`, are foreign and different applications must
encode them differently; see [component design](../architecture/component-design.md). `App`, `AppA`,
and `AppB` are fieldless, which is complete rather than a placeholder. The two arena tests' `App<'a>`
carries one field, the arena, because a provider draws it from the context during deserialization.

## Running an example

Each example runs from the repository root with `cargo test -p cgp-serde-tests <filter>`. Add
`-- --nocapture` to see what a test prints. The workspace pins Rust 1.98.1 in `rust-toolchain.toml` and
overrides `cgp` and `cgp-error-anyhow` with the `cgp` repository's `main` branch through
`[patch.crates-io]`, which the first build fetches; see
[crate layout](../architecture/crate-layout.md#build-facts). Once built, none of the tests needs a
network or any program outside the build. The table records what each did when run against the `v0.8.0` branch:

| Example | Filter | Result |
|---|---|---|
| [`basic`](basic.md) | `basic` | passes; the JSON and the round trip are asserted |
| [`messages`](messages.md) | `messages` | passes; prints two JSON documents without asserting them |
| [`arena_simplified`](arena-simplified.md) | `arena_simplified` | passes; the deserialized value is asserted |
| [`arena`](arena.md) | `arena::` | passes; the deserialized value is asserted |

The filter for the layered arena test is `arena::` rather than `arena`, because a bare `arena` also
matches `arena_simplified`. `cargo test --workspace` runs all four, and each compiles with no warnings.

## The catalog

The order is the order the examples teach in, from one round trip to a deserializer that draws a
service from its context.

- [basic.md](basic.md) — one struct serialized to JSON and read back, through the JSON `TryComputer`
  providers, with its bytes as hex.
- [messages.md](messages.md) — the two-application demo: nested data encoded as hex and RFC 3339 by
  one context, and as base64 and Unix timestamps by another.
- [arena-simplified.md](arena-simplified.md) — borrowed values deserialized into an arena the context
  supplies, with a test-local getter and deserializer, as in the announcement post.
- [arena.md](arena.md) — the same through the layered allocation crates, where the allocator is a
  wiring choice.

## What the examples leave out

The four tests exercise most of the library's providers but not all of them, so the examples are not a
tour of every provider. None of them runs the byte providers, `SerializeWithDisplay`,
`DeserializeWithFromStr`, `SerializeFrom`, `TrySerializeFrom`, or `DeserializeDefault`, none uses a
format other than JSON, and none feeds invalid input. [testing.md](../testing.md) records the coverage in full,
and the [reference](../reference/README.md) documents the rest of the providers from probes.

## Public material derived from this

The code for the "Wiring an application" and "Arena-allocating deserialization" pages of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and an examples section of the
repository README.
