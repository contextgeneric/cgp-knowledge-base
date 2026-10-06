# cgp-serde in the Projects section

The public section for cgp-serde, which rebuilds Serde's `Serialize` and `Deserialize` as CGP
components so that how each value type is encoded becomes a per-application wiring choice: four
example programs, the design behind the component split, the guides for wiring and writing
providers, one reference page per construct, and the comparison with Serde. The clearest
demonstration of the coherence bypass on a trait every Rust developer already knows.

- **URL** — <https://contextgeneric.dev/docs/projects/cgp-serde/>
- **Source** —
  [docs/projects/cgp-serde/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/projects/cgp-serde),
  written on the website's `v0.8.0` branch and not yet published
- **Ports** — [projects/cgp-serde/](../../projects/cgp-serde/README.md)
- **Repository** — [`cgp-serde`](https://github.com/contextgeneric/cgp-serde), documented on its
  `v0.8.0` branch
- **Verified against** — `cgp-serde` `v0.8.0` at commit `d89ee05`, with `cgp` `main` at `adc616c`
  through the workspace's patch, and at `bcc9fcc` for the `SerializeRecordFields` rename and the two
  variant provider pages, and `cargo-cgp` built from its source at commit `b6a6323`
- **Status** — Draft: 47 of about 52 pages written, listed in [What is written](#what-is-written);
  the two arena examples and three component pages wait on DC3
- **How it was made** — written by an agent from the project section; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What is written

**Forty-seven cgp-serde pages are written, all the pages that DC3 does not block**, and the section
index gained cgp-serde in its project list, five rows in its pattern table, and a line in its
evaluator route. Resources links the section beside the crate. `yarn build` passes with them, so
every link and anchor they carry resolves. They are:

- **Project** — `cgp-serde/index.md`.
- **Examples** — the index, `basic`, and `messages`.
- **Architecture** — the index, `serde-bridge`, `component-design`, `reentrant-providers`,
  `derive-free-records`, `context-services`, and `crate-layout`.
- **Guides** — `wiring-a-context`, `writing-a-provider`, `formats`, and `debugging-wiring`, under a
  generated category index.
- **Reference** — the index, with the provider tables and a *Looking for a name you don't see?*
  table; the 25 provider pages under `reference/providers/`; `SerializeWithContext`,
  `DeserializeWithContext`, and `CanDeserializeJsonString` under `reference/types/`; and `CanAlloc`
  under `reference/components/`, which carries no `#[derive_delegate]` and so is not blocked.
- **The comparison and the limitations** — `serde-comparison.md` and `limitations.md`.

**The pages not yet written** wait on DC3, and none is scaffolded as a stub. Pages that would link
them describe the idea in place or say the page is still being written:

- `examples/arena-simplified` and `examples/arena` wait on the cleanup of their tests. The
  architecture page `context-services` quotes the arena example's relevant entries with the unused
  JSON entries elided, and the debugging guide describes its allocator case without linking a page.
- `reference/components/can_serialize_value`, `can_deserialize_value`, and `has_arena` wait on the
  removal of their `#[derive_delegate]` attributes. `component-design` shows the two components'
  method signatures rather than their declarations, and `AllocateWithArena` describes the getter in
  prose.

The writing turned up several facts a later revision must respect:

- **Every run and diagnostic was re-produced.** The four examples' tests were run offline and
  passed, and `messages` asserts the two documents the pages quote. Each *Try a change* result, each
  diagnostic, and each claim the pages add beyond the records was re-run in a probe crate at
  `~/.cache/cgp-probes/serde-probe`, whose sources are kept under `reports/probes/cgp-serde-pages/`
  in the workspace. The postcard claim is the one taken from the records alone, since the crate
  could not be fetched offline.
- **The `E0275` cases are reshaped when checked.** A provider that depends on itself and a recursive
  type both report `[CGP-E010]` through `check_components!`, from the published `cargo-cgp` as well
  as the source build; at a call site with no check, the raw overflow stays. The project's
  [debugging guide](../../projects/cgp-serde/guides/debugging-wiring.md) is corrected to match.
- **A context-defined namespace shares wiring.** The wiring guide's last step shows `AppA` and `AppB`
  sharing entries through a namespace of the reader's own, which a probe confirmed, with each context
  still opening the component and a rebinding rejected as `[CGP-E005]`. It is advice for the reader,
  not the library's `CgpSerdeNamespace`, and the [wiring
  record](../../projects/cgp-serde/guides/wiring-a-context.md#share-wiring-between-contexts) carries it.
- **Source links point at `main`**, per the writing guide, so until the `v0.8.0` branch merges they
  show the release's `UseDelegate` tables. Links to files that exist only on `v0.8.0` do not
  resolve until then: the two variant provider pages' sources, and the example pages' sources under
  `crates/cgp-serde-examples/`.
- **The variant provider pages were written with the providers.** `serialize_variant_fields` and
  `deserialize_variant_fields` state only what the `variants` test suite asserts, and present the
  `'static` limit and the single enum form as limits a reader must know before choosing them.
- **The install instructions assume the merge too.** The index tells a reader to depend on the
  crates from the repository by git, since the crates.io release is built on an older CGP.
- **Every example page has a *The problem* section before its code**, per [the writing
  guide](../writing-guides/project.md#then-it-states-the-problem): the task, what makes it hard, and
  a *Without CGP* part that concedes where a shell script, plain Rust, or Serde's derive is simpler
  and names the requirement that tips the balance. A revision keeps it fair to the alternative.
- **No public page lists cgp-serde's defects or missing features.** Where a defect shapes how a
  provider is used, the provider's page states the behavior and routes the reader in *When to use
  it*: `SerializeBytes` sends JSON users to the text encodings, and `DeserializeWithFromStr` states
  the inputs it reads. The defects themselves stay in [issues.md](../../projects/cgp-serde/issues.md).
- **The comparison's two judging sections want the author's read.** `serde-comparison.md` is a
  Projects page, but its *What each approach costs* and *When plain Serde is the better choice*
  judge another project's tool, the same reason those sections of every Comparisons page are on the
  author's list in [../AGENTS.md](../AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes).

## What it covers

cgp-serde makes the case for CGP on ground the reader already stands on. Serde gives a type one
`Serialize` implementation, chosen by whoever owns the type, so an application that wants bytes as
hex where another wants base64 has to wrap the type or fork the implementation. cgp-serde moves the
value out of `Self` into a parameter, so the implementation is chosen by the context instead, and
two applications encode the same value differently by a few wiring lines. It also shows that a type
can be serialized with no serialization derive at all, and that a deserializer can draw a service,
an arena, from its context.

The section has no measured search demand to answer: the announcement post draws impressions at an
average position of 16.8 and converts at 0.13%, and the *serde* query cluster sits below position 24
with no clicks, per [seo.md](../seo.md). So the index is written for a reader who arrives from the
section index or a link, not for a search result.

The section serves the **evaluator** first: the question "can CGP do something real" is answered
most directly by a library that replaces part of Serde. So the index opens on the two-application
result, and the comparison with Serde and the limitations page are as prominent as the examples.
Every context in the project is environmental and every component is parameter-targeted: `AppA` and
`AppB` stand for two applications' choices, and the serialized value is a parameter. The first
example page says so beside the code, since a reader arriving from Serde expects the value to be
`Self`.

**The index must say on its first screen that cgp-serde is a proof of concept**, which it describes
itself as, and state its scope in the terms a Serde user asks about: that it replaces Serde's
per-type implementations while keeping Serde's data model and formats, and that its generic
providers cover structs with named fields, enums whose variants each hold one value, and types that
already implement Serde's traits. It does
not list the features it lacks; those are records in the project's `issues.md`.

## The pages

The index, four example pages and their index, 7 architecture pages, 4 guides, 33 reference pages
with the reference index, the comparison, and the limitations page: 52 in all, of which 47 are
written.

### Index

From the [project README](../../projects/cgp-serde/README.md): the constraint Serde imposes, the
two-application payoff shown immediately, the derive-free result, the status, and the route into the
examples. The index should work on its own for a reader who reads nothing else.

### Examples

One page per example in [examples/](../../projects/cgp-serde/examples/README.md), in its teaching
order, with `examples/index.md` from that README. The four examples live in the
`cgp-serde-examples` crate as Cargo example targets and are the repository's only runnable
programs; the tests in `cgp-serde-tests` get no pages.

- `basic` — one struct round-tripped through JSON by the JSON providers, with its bytes as hex and
  errors through the anyhow backend. The pattern: serialization as a wired operation, with the error
  type chosen by the context.
- `messages` — one nested archive encoded by two contexts that differ in three entries. The pattern:
  two applications choosing overlapping providers for the same type without a coherence conflict,
  and the entries a traversal needs. Its record already carries the one *Try a change* this section
  most needs: removing the `i64` entry and reading the root cause `cargo cgp check` reports.
- `arena-simplified` — borrowed values deserialized into a context-supplied arena through a
  local getter and deserializer. The page presents itself as the smaller form, and says what
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
- **`reference/providers/`, 25 pages** — the twenty-one serialization and deserialization
  providers, from `UseSerde` to `DeserializeAndAllocate`, then the three JSON providers and
  `AllocateWithArena`. Each page's *Pairing* section names the provider for the other direction, or
  says there is none, and its *Context dependencies* section names what the provider re-enters the
  context for.

### The comparison and the limitations

- **`serde-comparison.md`** — from
  [serde-comparison.md](../../projects/cgp-serde/serde-comparison.md): what cgp-serde keeps from
  Serde, what it adds, what it lacks, how Serde's idioms map onto wiring, and when plain Serde is
  the better choice. This page is the evaluator's destination from the index and must keep its last
  section.
- **`limitations.md`** — the high-level limits of the design and status, written from the README and
  the architecture: a proof of concept, which part of Serde it replaces and which it keeps, the
  kinds of data type its generic providers cover, and the formats that fit its output. It names no
  bugs and no unimplemented features; those stay in [issues.md](../../projects/cgp-serde/issues.md).

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
- **Clean up the two arena examples** before their pages quote them: `arena.rs` wires two JSON
  handler entries it never uses, and `arena_simplified.rs` repeats a check in a second table.
  The local getter in `arena_simplified.rs` can become an `#[implicit]` argument, which a probe
  confirmed.
- **Publish a `CgpSerdeNamespace`**, recommended rather than required. It is a design decision about
  what the defaults should be, and it is the library improvement that would most strengthen the
  section: the `messages` payoff is sharper when the shared wiring is one `namespace` line and the
  two applications differ only in the entries that matter. **If it is built, revise `messages`,
  `basic`, and the wiring guide against it together**, since all three are written against the
  wiring as it stands; the guide's last step shows a reader-defined namespace, which the library's
  own would replace.

### Release conditions

**A cgp-serde release built on `cgp` 0.8.0.** The crates on crates.io and the repository's `main`
are 0.2.0, built against `cgp` 0.7.0, and the `v0.8.0` branch still carries that version, so the
release needs a new version number. The `v0.8.0` branch must also be the default before source links
point at it.

## The source post

[cgp-serde: Serde as CGP components](../blog/cgp-serde-release.md) carries a notice at its top linking
the cgp-serde section, and so does the [RustLab talk transcript](../blog/rustlab-2025-coherence.md),
which used the library as its live demonstration; the author settled that the talk gets one. The
`basic` and `messages` pages link the announcement post back at the section that presents each, and
`messages` also links the talk.


## Maintaining it

**The comparison and the limitations page change only where a limit stops being true**; neither is
trimmed as the library matures. And if the namespace lands after the pages are written, revise
`messages`, `basic`, and the wiring guide together rather than patching one, since the three show
the same wiring.
