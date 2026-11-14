# Announcing Context-Generic Programming (Early Preview)

CGP's launch post: the paradigm's first public introduction and a plan for 2025, nearly all of it
since done, several items by mechanisms the post did not foresee.

- **URL**: <https://contextgeneric.dev/blog/early-preview-announcement>
- **Source**: [blog/2024-12-19-early-preview-announcement.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2024-12-19-early-preview-announcement.md)
- **Published**: 19 December 2024, tagged `release`
- **Release**: describes [v0.2.0](../../releases/v0-2-0.md), the version current at launch
- **Status**: Historical

## What it covers

A project announcement with almost no code, in three parts:

- **What CGP is:** context-generic programs that work with any `Self` type, provider traits that lift
  the coherence restrictions, and an expressiveness comparison to OOP patterns such as inheritance and
  mixins, conceding that CGP programs "may look very different from regular Rust programs, and appear
  intimidating to even experienced Rust programmers."
- **The origin story, written down nowhere else:** CGP began around July 2022 while the author worked
  on the [Hermes IBC relayer](https://github.com/informalsystems/hermes) at Informal Systems, whose
  code turned on one monolithic `ChainHandle` trait with dozens of methods. The techniques started as
  blanket implementations used as dependency injection, so generic code required only the dependencies
  it needed, and were extracted into the [Hermes SDK](https://github.com/informalsystems/hermes-sdk),
  which the post offers as evidence the approach scales: the two codebases implement the same
  functionality and look almost nothing alike.
- **A plan for 2025 in eight parts:** finish the book, improve error diagnostics, document the `cgp`
  crate, speak at conferences, improve the macros, build developer tooling, implement extensible
  records and variants, and write more documentation.

It closes with links to its launch discussions on Reddit, Lobsters, and Hacker News.

## How it relates to the knowledge base

- **The origin story:** the monolithic-trait pain in
  [message.md](../../communication-strategy/message.md#the-problems-cgp-removes) is the concrete
  problem CGP was built for, and Hermes SDK is the adopter
  [evidence.md](../../communication-strategy/evidence.md) calls the strongest social proof. The
  dependency injection through blanket impls is [impl-side
  dependencies](../../cgp/concepts/impl-side-dependencies.md).
- **The launch discussions:** part of the reception
  [evidence.md](../../communication-strategy/evidence.md) summarizes without linking or quoting, per the
  [public-repository rule](../../AGENTS.md#this-repository-is-public); its "verbose or
  over-engineered", "prior work reinvented", and "the name does not communicate" patterns appear in
  them. Revise CGP's framing from that summary.

## Where it diverges from CGP v0.8.0

The post has no code, so nothing is syntactically stale; every item of the plan has moved:

- **Error diagnostics.** The post's answer was a patch to `rustc`
  ([rust#134346](https://github.com/rust-lang/rust/issues/134346),
  [rust#134348](https://github.com/rust-lang/rust/pull/134348)) and a forked compiler for serious CGP
  use. That route was abandoned. The answer is [`cargo-cgp`](../../cargo-cgp/README.md), a cargo
  subcommand that rewrites CGP errors outside the compiler, with the
  [`IsProviderFor`](../../cgp/reference/traits/is_provider_for.md) technique from v0.4.0 that made the
  causes visible. **No fork of the Rust compiler is needed, and none ever became needed**; read as
  current, this advice is the most actively misleading thing on the site.
- **Developer tooling.** The post speculates about analyzers and IDE features "similar to Rust
  Analyzer", over more than a year. `cargo-cgp` delivered the diagnostics, and its
  [`expand` command](../../cargo-cgp/reference/usage.md) the introspection; the Rust Analyzer
  integration is an on-save check backend rather than bespoke IDE features.
- **Public speaking.** Delivered: the [RustLab 2025 talk](rustlab-2025-coherence.md).
- **Extensible records and variants.** Delivered in v0.4.2, in the
  [four-part series](extensible-datatypes-part-1.md), and now in
  [extensible records](../../cgp/concepts/extensible-records.md) and
  [extensible variants](../../cgp/concepts/extensible-variants.md).
- **Macro quality.** The post describes macros "written in haste" that "just panic" on bad input, and
  names const generics and associated constants as failure cases. Associated `const` items landed in
  v0.4.0; const *generic parameters* on a component trait remain rejected, for the structural reason in
  [`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md).
- **The book.** [CGP Patterns](https://patterns.contextgeneric.dev/) was not finished;
  [patterns-book.md](../patterns-book.md) records which chapters are still current. The live
  Introduction says the book has not been updated for a while; the `v0.8.0` branch leaves it out as a
  legacy resource.

## Maintaining it

Leave the post alone: its value is that it records what the project believed in December 2024. If the
compiler-fork advice is judged harmful, the one claim a reader could act on to their cost, the remedy
is a dated editor's note at the top pointing to [`cargo-cgp`](../../cargo-cgp/reference/installation.md),
not an edit to the body; that is the user's call.
