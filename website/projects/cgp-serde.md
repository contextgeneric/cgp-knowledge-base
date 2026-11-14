# cgp-serde in the Projects section

The public section for cgp-serde, which rebuilds Serde's `Serialize` and `Deserialize` as CGP
components so that how each value type is encoded becomes a per-application wiring choice: example
programs, the design behind the component split, the guides for wiring and writing providers, one
reference page per construct, and the comparison with Serde. The clearest demonstration of the
coherence bypass on a trait every Rust developer already knows.

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
- **Status** — Draft: 49 of 54 pages written, listed in [What is written](#what-is-written); the two
  arena examples and three component pages wait on its [code prerequisites](#code-prerequisites)
- **How it was made** — written by an agent from the project section; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What is written

Forty-nine pages, all those the code prerequisites do not block, with cgp-serde in the section index's
project list, pattern table, and evaluator route, and on Resources beside the crate. The site build
passes with them.

- **Project** — `cgp-serde/index.md`.
- **Examples** — the index, `basic`, `messages`, and `events`.
- **Architecture** — the index, `serde-bridge`, `component-design`, `reentrant-providers`,
  `derive-free-records`, `context-services`, and `crate-layout`.
- **Guides** — `wiring-a-context`, `writing-a-provider`, `formats`, and `debugging-wiring`, under a
  generated category index.
- **Reference** — the index, with the provider tables and a *Looking for a name you don't see?*
  table; the 26 provider pages under `reference/providers/`; `SerializeWithContext`,
  `DeserializeWithContext`, and `CanDeserializeJsonString` under `reference/types/`; and `CanAlloc`
  under `reference/components/`, which carries no `#[derive_delegate]`. The JSON `Code` types,
  `SerializeJson` and `DeserializeJson`, are documented on the pages of the providers wired for them.
- **The comparison and the limitations** — `serde-comparison.md` and `limitations.md`.

Pages that would link an unwritten page describe the idea in place: `context-services` quotes the
arena example's entries with its unused JSON entries elided, the debugging guide describes its
allocator case without a link, `component-design` shows the two serialization components' method
signatures rather than their declarations, and `AllocateWithArena` describes the arena getter in
prose.

A revision must respect these facts:

- **Every run and diagnostic was reproduced.** The examples' tests were run offline and passed, and
  `messages` and `events` assert the documents the pages quote. Each *Try a change* result, diagnostic,
  and claim the pages add beyond the records was re-run in a probe crate; the postcard claim is the one
  taken from the records alone, since the crate could not be fetched offline.
- **The `E0275` cases are reshaped when checked.** A provider that depends on itself and a recursive
  type both report `[CGP-E020]` through `check_components!`; at a call site with no check, the raw
  overflow stays, as the project's
  [debugging guide](../../projects/cgp-serde/guides/debugging-wiring.md) states.
- **The wiring guide's last step shares wiring through a namespace of the reader's own**, which a probe
  confirmed: each context still opens the component, and a rebinding is rejected as `[CGP-E011]`. It
  is advice for the reader, not a library namespace, and the
  [wiring record](../../projects/cgp-serde/guides/wiring-a-context.md#share-wiring-between-contexts)
  carries it.
- **The variant provider pages state only what the `variants` test suite asserts.**
  `serialize_variant_fields` and `deserialize_variant_fields` present the `'static` limit and the
  single enum form as limits a reader must know before choosing them. `serialize_unit` came with the
  empty-variant support, and the `events` page's *Try a change* diagnostic was re-run then.
- **Source links point at `main`**, so until the `v0.8.0` branch merges they show the release's
  `UseDelegate` tables, and links to files only on `v0.8.0` do not resolve: the two variant provider
  pages' sources and the example pages' sources under `crates/cgp-serde-examples/`.
- **The install instructions assume that merge too**: the index tells a reader to depend on the crates
  from the repository by git, since the crates.io release is built on an older CGP.
- **The comparison's two judging sections want the author's read.** *What each approach costs* and
  *When plain Serde is the better choice* judge another project's tool, the reason those sections of
  every Comparisons page are on the author's list in
  [../AGENTS.md](../AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes).

## What it covers

cgp-serde moves the serialized value out of `Self` into a parameter, so the context chooses each
type's encoding, and two applications encode the same value differently by a few wiring lines where
Serde would need a wrapper or a fork. It also shows a type serialized with no serialization derive,
and a deserializer drawing a service, an arena, from its context.

**The section serves the evaluator first**, so the index opens on the two-application result, and the
comparison and the limitations page are as prominent as the examples. The section answers no measured
search demand, per [seo.md](../seo.md), so the index is written for a reader arriving from the section
index or a link. Every context is environmental and every component parameter-targeted, which the
first example page says beside the code, since a reader arriving from Serde expects the value to be
`Self`.

**The index says on its first screen that cgp-serde is a proof of concept**, and states its scope in a
Serde user's terms: it replaces Serde's per-type implementations while keeping Serde's data model and
formats, and its generic providers cover structs with named fields, enums whose variants each hold one
value, and types that already implement Serde's traits. It does not list the features it lacks, and
it works for a reader who reads nothing else.

**The examples are the `cgp-serde-examples` crate's Cargo example targets**, the repository's only
runnable programs; the tests in `cgp-serde-tests` get no pages.

**`serde-comparison.md` must keep its *When plain Serde is the better choice* section**, since the
page is the evaluator's destination from the index.

## The pages still to write

- **`examples/arena-simplified`** — borrowed values deserialized into a context-supplied arena through
  a local getter and deserializer. The page presents itself as the smaller form and says what the
  layered form adds.
- **`examples/arena`** — the same through the layered allocation crates, with the allocator as a
  wiring entry. The pattern: a provider drawing a runtime service from the context.
- **`reference/components/can_serialize_value`, `can_deserialize_value`, and `has_arena`**, which show
  each component's definition.

## Prerequisites

### Code prerequisites

**The repository needs these changes, each recorded in the project's
[missing features](../../projects/cgp-serde/issues.md#missing-features) and
[housekeeping](../../projects/cgp-serde/issues.md#housekeeping):**

- **Drop the three `#[derive_delegate(UseDelegate<…>)]` attributes** on the two serialization
  components and on `HasArena`, since their pages show each definition. Every context on the branch
  dispatches with `open`, so the attributes serve only a downstream user still building `UseDelegate`
  tables, and that breakage is accepted. This blocks the three component pages.
- **Clean up the two arena examples** before their pages quote them: `arena.rs` wires two JSON handler
  entries it never uses, and `arena_simplified.rs` repeats a check in a second table. Its local getter
  can become an `#[implicit]` argument, which a probe confirmed.
- **Publish a `CgpSerdeNamespace`**, recommended rather than required: a design decision about the
  defaults that would most strengthen the section, since the `messages` payoff is sharper when the
  shared wiring is one `namespace` line. **If it is built, revise `messages`, `basic`, and the wiring
  guide against it together**, since all three show the wiring as it stands, and the guide's
  reader-defined namespace would give way to the library's.

### Release conditions

**A cgp-serde release built on `cgp` 0.8.0.** The crates on crates.io and the repository's `main` are
0.2.0, built against `cgp` 0.7.0, and the `v0.8.0` branch still carries that version, so the release
needs a new version number. The `v0.8.0` branch must also be the default before source links point at
it.

## The source post

[cgp-serde: Serde as CGP components](../blog/cgp-serde-release.md) carries a notice at its top linking
the section, and so does the [RustLab talk transcript](../blog/rustlab-2025-coherence.md), which used
the library as its live demonstration. The `basic` and `messages` pages link the announcement post
back at the section that presents each, and `messages` also links the talk.

## Maintaining it

- **The comparison and the limitations page change only where a limit stops being true**; neither is
  trimmed as the library matures.
- **If the namespace lands after the pages, revise `messages`, `basic`, and the wiring guide
  together**, since the three show the same wiring.
