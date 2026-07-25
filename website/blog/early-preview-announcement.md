# Announcing Context-Generic Programming (Early Preview)

CGP's launch post, introducing the paradigm to the public for the first time and laying out a year of
planned work — nearly all of which has since been done, in several cases by mechanisms the post did
not foresee.

- **URL** — <https://contextgeneric.dev/blog/early-preview-announcement>
- **Source** — [blog/2024-12-19-early-preview-announcement.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2024-12-19-early-preview-announcement.md)
- **Published** — 19 December 2024, tagged `release`
- **Release** — describes [v0.2.0](../../releases/v0-2-0.md), the version current at launch
- **Status** — Historical

## What it covers

The post is a project announcement rather than a technical piece, and it contains almost no code. It
opens with a prose overview of what CGP is — context-generic programs that work with any `Self` type,
provider traits that lift the coherence restrictions, and an expressiveness comparison to OOP patterns
like inheritance and mixins — while conceding up front that CGP programs "may look very different from
regular Rust programs, and appear intimidating to even experienced Rust programmers."

The middle section is the project's origin story, and it is the only place this history is written
down. CGP began around July 2022 while the author was working on the
[Hermes IBC relayer](https://github.com/informalsystems/hermes) at Informal Systems, where the
codebase turned on a single monolithic `ChainHandle` trait carrying dozens of methods. The techniques
that became CGP started as an attempt to replace that trait with blanket implementations used as
dependency injection, so generic code could require the minimal subset of dependencies it actually
needed. Those techniques were gradually extracted into the
[Hermes SDK](https://github.com/informalsystems/hermes-sdk), which the post offers as evidence that
the approach scales: the two codebases implement the same functionality and look almost nothing alike.

The remainder is a plan for 2025 in seven parts — finish the book, improve error diagnostics, document
the `cgp` crate, speak at conferences, improve the macros, build developer tooling, implement
extensible records and variants, and write more documentation. It closes with links to the launch
discussions on [Reddit](https://www.reddit.com/r/rust/comments/1hkzaiu/announcing_contextgeneric_programming_a_new/),
[Lobsters](https://lobste.rs/s/a5wfid/context_generic_programming), and
[Hacker News](https://news.ycombinator.com/item?id=42498176).

## How it relates to the knowledge base

The origin story is the source for a fact the communication strategy leans on: the monolithic-trait
pain in [problems-solved.md](../../communication-strategy/problems-solved.md) is not hypothetical but
the concrete problem CGP was built to solve, and Hermes SDK is the flagship real-world adopter that
[attention-and-engagement.md](../../communication-strategy/attention-and-engagement.md) argues is the
strongest available social proof. The dependency-injection-through-blanket-impls technique the post
describes discovering is [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md).

The launch discussions this post links to are the primary evidence base for CGP's public reception,
analyzed in [attention-and-engagement.md](../../communication-strategy/attention-and-engagement.md) —
the "verbose / over-engineered," "isn't this just X reinvented," and "the name does not communicate"
patterns all come from this thread. Anyone revising CGP's framing should read the linked discussions
alongside that analysis rather than only the summary.

## Where it diverges from CGP v0.8.0

The post contains no code, so nothing in it is syntactically stale. What has changed is the *plan*,
and every item on it has moved:

- **Error diagnostics.** The post's answer was a patch to `rustc` ([rust#134346](https://github.com/rust-lang/rust/issues/134346),
  [rust#134348](https://github.com/rust-lang/rust/pull/134348)) and a forked compiler for serious CGP
  use. That route was abandoned. The actual answer arrived as
  [`cargo-cgp`](../../cargo-cgp/README.md), a cargo subcommand that rewrites CGP errors outside the
  compiler, plus the [`IsProviderFor`](../../cgp/reference/traits/is_provider_for.md) technique
  shipped in v0.4.0 that made the causes visible in the first place. **No fork of the Rust compiler
  is needed, and never became needed** — the post's advice on this point is the most actively
  misleading thing on the site if read as current.
- **Developer tooling.** The post speculates about analyzers and IDE features "similar to Rust
  Analyzer," estimating over a year. `cargo-cgp` delivered the diagnostic half, and its
  [`expand` command](../../cargo-cgp/reference/usage.md) the introspection half; the Rust Analyzer
  integration exists as an on-save check backend rather than as bespoke IDE features.
- **Public speaking.** Delivered: the [RustLab 2025 talk](rustlab-2025-coherence.md).
- **Extensible records and variants.** Delivered in v0.4.2, documented across the
  [four-part series](extensible-datatypes-part-1.md) and now in
  [extensible records](../../cgp/concepts/extensible-records.md) and
  [extensible variants](../../cgp/concepts/extensible-variants.md).
- **Macro quality.** The post describes macros "written in haste" that "just panic" on bad input, and
  names const generics and associated constants as known failure cases. Associated `const` items in
  CGP traits landed in v0.4.0; const *generic parameters* on a component trait remain rejected, for
  the structural reason recorded in [`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md).
- **The book.** [CGP Patterns](https://patterns.contextgeneric.dev/) was not finished and has not
  been updated for some time, a caveat the site's own [Introduction](../site-structure.md) now
  carries.

## Maintaining it

Leave the post alone. It is a dated announcement whose value is precisely that it records what the
project believed in December 2024, and rewriting the plan section would erase the evidence of how far
the project has come. If the compiler-fork advice is judged actively harmful — it is the one claim a
reader could act on to their cost — the right remedy is a dated editor's note at the top pointing to
[`cargo-cgp`](../../cargo-cgp/reference/installation.md), not an edit to the body. That is a call for
the user to make.
