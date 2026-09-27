# cgp-serde in the Projects section

The public section for cgp-serde, which rebuilds Serde's `Serialize` and `Deserialize` as CGP
components so that how each value type is encoded becomes a per-application wiring choice: four
example programs, the design behind the component split, the guides for wiring and writing
providers, one reference page per construct, and the comparison with Serde. The clearest
demonstration of the coherence bypass on a trait every Rust developer already knows.

- **Planned URL** — `https://contextgeneric.dev/docs/projects/cgp-serde/`
- **Ports** — [projects/cgp-serde/](../../projects/cgp-serde/README.md)
- **Repository** — [`cgp-serde`](https://github.com/contextgeneric/cgp-serde), documented on its
  `v0.8.0` branch
- **Status** — planned; no page written. The component reference pages wait on DC3

## What it covers

cgp-serde makes the case for CGP on ground the reader already stands on. Serde gives a type one
`Serialize` implementation, chosen by whoever owns the type, so an application that wants bytes as
hex where another wants base64 has to wrap the type or fork the implementation. cgp-serde moves the
value out of `Self` into a parameter, so the implementation is chosen by the context instead, and
two applications encode the same value differently by a few wiring lines. It also shows that a type
can be serialized with no serialization derive at all, and that a deserializer can draw a service,
an arena, from its context.

The section serves the **evaluator** first: the question "can CGP do something real" is answered
most directly by a library that replaces part of Serde. So the index opens on the two-application
result, and the comparison with Serde and the limitations page are as prominent as the examples.
Every context in the project is environmental and every component is parameter-targeted: `AppA` and
`AppB` stand for two applications' choices, and the serialized value is a parameter. The first
example page says so beside the code, since a reader arriving from Serde expects the value to be
`Self`.

**The index must say on its first screen that cgp-serde is a proof of concept**, which it describes
itself as, with the gaps a Serde user will look for first: no generic enum support, no tuple
structs, none of Serde's attributes, and no length-prefixed binary formats.

## The pages

Four example pages, 7 architecture pages, 4 guides, about 30 reference pages, the comparison, and
the limitations page: about 48 in all.

### Index

From the [project README](../../projects/cgp-serde/README.md): the constraint Serde imposes, the
two-application payoff shown immediately, the derive-free result, the status, and the route into the
examples. The index should work on its own for a reader who reads nothing else.

### Examples

One page per test in [examples/](../../projects/cgp-serde/examples/README.md), in its teaching
order, with `examples/index.md` from that README. The tests are the repository's only runnable
programs, and each page runs its test with `--nocapture` where the test prints.

- `basic` — one struct round-tripped through JSON by the JSON providers, with its bytes as hex and
  errors through the anyhow backend. The pattern: serialization as a wired operation, with the error
  type chosen by the context.
- `messages` — one nested archive encoded by two contexts that differ in three entries. The pattern:
  two applications choosing overlapping providers for the same type without a coherence conflict,
  and the entries a traversal needs. Its record already carries the one *Try a change* this section
  most needs: removing the `i64` entry and reading the root cause `cargo cgp check` reports.
- `arena-simplified` — borrowed values deserialized into a context-supplied arena through a
  test-local getter and deserializer. The page presents itself as the smaller form, and says what
  the layered form adds.
- `arena` — the same through the layered allocation crates, with the allocator as a wiring entry.
  The pattern: a provider drawing a runtime service from the context, and the allocator as a wiring
  choice.

### Architecture

One page per document in [architecture/](../../projects/cgp-serde/architecture/README.md), with the
one-page design as the index: `serde-bridge`, `component-design`, `reentrant-providers`,
`derive-free-records`, `context-services`, and `crate-layout`. `component-design` is where the
value's move out of `Self` is explained; it links the *Modularity Hierarchy* Concepts page for why
that move changes who chooses the implementation, rather than re-arguing it.

### Guides

`wiring-a-context`, `writing-a-provider`, `debugging-wiring`, and `formats`, from
[guides/](../../projects/cgp-serde/guides/README.md). `debugging-wiring` quotes `cargo cgp check`
output and carries the canonical qualification.

### Reference

One page per construct, split from the eleven family documents in
[reference/](../../projects/cgp-serde/reference/README.md). The JSON `Code` types, `SerializeJson`
and `DeserializeJson`, are documented on the pages of the providers wired for them; everything else
gets a page. Enumerate against the source when porting; the groups are:

- **`reference/components/`, 4 pages** — `CanSerializeValue`, `CanDeserializeValue`, `CanAlloc`, and
  `HasArena`.
- **`reference/types/`, 3 pages** — the adapters `SerializeWithContext` and
  `DeserializeWithContext`, and the `CanDeserializeJsonString` blanket trait.
- **`reference/providers/`, 23 pages** — the nineteen serialization and deserialization providers,
  from `UseSerde` to `DeserializeAndAllocate`, then the three JSON providers and
  `AllocateWithArena`. Each page's *Pairing* section names the provider for the other direction, or
  says there is none, and its *Context dependencies* section names what the provider re-enters the
  context for.

### The comparison and the limitations

- **`serde-comparison.md`** — from
  [serde-comparison.md](../../projects/cgp-serde/serde-comparison.md): what cgp-serde keeps from
  Serde, what it adds, what it lacks, how Serde's idioms map onto wiring, and when plain Serde is
  the better choice. This page is the evaluator's destination from the index and must keep its last
  section.
- **`limitations.md`** — from [issues.md](../../projects/cgp-serde/issues.md): the byte round-trip,
  owned bytes, borrowed strings, and undeclared lengths, then the missing features, including
  recursive data types, which fail to compile through the generic providers.

## Prerequisites

### Code prerequisites

**DC3 in [tasks.md](../tasks.md) carries the changes, each recorded in the project's [missing
features](../../projects/cgp-serde/issues.md#missing-features) and
[housekeeping](../../projects/cgp-serde/issues.md#housekeeping):**

- **Drop the three `#[derive_delegate(UseDelegate<…>)]` attributes** on the two serialization
  components and on `HasArena`, since their reference pages show each component's definition. Every
  context on the branch dispatches with `open`, so the attributes serve only a downstream user still
  building `UseDelegate` tables, and that breakage is accepted. This blocks the three component
  pages.
- **Clean up the two arena tests** before their example pages quote them: `arena.rs` wires two JSON
  handler entries its test never uses, and `arena_simplified.rs` repeats a check in a second table.
  The test-local getter in `arena_simplified.rs` can become an `#[implicit]` argument, which a probe
  confirmed.
- **Publish a `CgpSerdeNamespace`**, recommended rather than required. It is a design decision about
  what the defaults should be, and it is the library improvement that would most strengthen the
  section: the `messages` payoff is sharper when the shared wiring is one `namespace` line and the
  two applications differ only in the entries that matter. **If it is built, write `messages`,
  `basic`, and the wiring guide against it** rather than revising them afterwards.

### Release conditions

**A cgp-serde release built on `cgp` 0.8.0.** The crates on crates.io and the repository's `main`
are 0.2.0, built against `cgp` 0.7.0, and the `v0.8.0` branch still carries that version, so the
release needs a new version number. The `v0.8.0` branch must also be the default before source links
point at it.

## The source post

[cgp-serde: Serde as CGP components](../blog/cgp-serde-release.md) gets a pointer to the cgp-serde
index when the section publishes. The [RustLab talk transcript](../blog/rustlab-2025-coherence.md)
used the library as its live demonstration; whether it gets a pointer too is the author's decision,
since the settled rule covers the post a section grew out of.

## Maintaining it

**The comparison and the limitations page change only as items are fixed**; neither is trimmed as
the library matures. And if the namespace lands after the pages are written, revise `messages`,
`basic`, and the wiring guide together rather than patching one, since the three show the same
wiring.
