# Using an incoherent, dictionary-passing style Rust today

An unpublished post of about 9,300 words reading CGP against the Rust language-design discussion of
dictionary-passing style, incoherent traits, and contexts and capabilities, and arguing that CGP is a
working implementation strategy for a substantial fragment of those designs, on stable Rust today at a
stated cost.

- **URL**: none; the post is not published
- **Source**: `blog/2026-11-25-incoherent-rust-today.md` on the `incoherent-rust` branch of the
  [website repository](https://github.com/contextgeneric/contextgeneric.dev), not on `main`
- **Date in filename**: 2026-11-25, set when the author approved the first revision; the draft dates
  from 2026-03-30
- **Status**: Draft
- **Publication**: after the documents it links, *Rust's own proposals* revised and a new *Traits
  without coherence* comparison, are published

## Why this post is different

**It is the only CGP writing aimed at the [language-design
reader](../../communication-strategy/readers.md#the-language-design-and-compiler-team-reader)**:
compiler-team members and the authors of Rust's design posts on traits and coherence, for whom
nothing needs simplifying and any imprecision shows. Every other post argues CGP is *useful*; this
one argues it is *evidence*.

**It is also the only post whose value decays.** The discussion it answers is dated, so its usefulness
depends on whether that conversation is live, which makes its timing a real decision.

## What it covers

Five movements, long because each is taken at the precision its audience expects:

- **The discussion it joins**, as the author's own reading of public material, with the caveat that
  the author may be missing context: Nadrieril's posts on explicit trait proofs and on traits carrying
  values, Boxy's *An Incoherent Rust*, and Tyler Mandry's context-and-capabilities work, read as one
  conversation with two separable goals, formalizing the trait system and building features on it,
  which has since become the types team's Dictionary Passing Style Experiment and a line of work on
  cyclic trait impls. The post coins **TIR** (a traitless intermediate
  representation) and **Incoherent Rust** (the envisioned language), and analyzes the goals
  separately so one's feasibility does not decide the other.
- **A CGP primer for compiler-team readers:** no analogies or progressive disclosure, straight to
  provider traits with an explicit context parameter. It separates the two levels of coherence bypass
  (overlap through the provider-trait indirection, orphans by moving the target into a parameter) and
  asks whether CGP "truly solves" the orphan problem rather than asserting it.
- **Incoherent Rust desugared into CGP**, feature by feature: incoherent traits, named impls,
  incoherent trait bounds, incoherent bounds in a struct, and impl-specific bindings. Its sharpest idea
  is that **the context type is the dictionary**, one top-level dictionary carrying the others, which
  makes dependency instantiation tractable. A runtime dictionary does not need an instantiation order,
  but CGP's wiring rejects a cycle with `E0275`, so recursive providers need a provider written for the
  concrete context, which the post presents as a use case for the cyclic-impl work. Context and
  capabilities is a special case, worked as an arena-allocating deserializer.
- **Limitations, which make the post credible:** a `&self` context cannot supply mutable or owned
  values without interior mutability, and all bindings are declared in one place, so the nested
  dynamically scoped bindings *scoped impls* envision have no CGP equivalent short of something like
  inheritance. Centralized bindings may be a virtue, being easier to reason about, but are conceded as
  a restriction.
- **What CGP adds and the ideas it suggests:** named impls as first-class types and explicit context
  types, then incoherent functions, zero-arity traits, and abstract types as ideas for Incoherent Rust;
  a related-work paragraph that links the *Traits without coherence* comparison, with lessons drawn
  from Haskell, Cairo, Scala, modular implicits, and Boxy's sketch; and a conclusion split into what CGP
  solves, partially solves, and does not solve.

**The conclusion's close:** if these features land, parts of the CGP library become unnecessary while
its patterns stay valuable, and CGP never aimed to be a framework developers depend on indefinitely.

## How it relates to the knowledge base

- **Concepts:** [coherence](../../cgp/concepts/coherence.md) and
  [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), with the two-level
  bypass matching the tiers of the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md);
  context-as-dictionary is [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md) for a
  reader who knows dictionaries; the capabilities section rests on
  [implicit arguments](../../cgp/concepts/implicit-arguments.md) and
  [`HasField`](../../cgp/reference/traits/has_field.md); the abstract-types divergence is
  [abstract types](../../cgp/concepts/abstract-types.md); the arena example is the deserialization half
  of [modular serialization](../../examples/modular-serialization.md).
- **Related work:** [ML modules](../../related-work/ml-modules.md),
  [implicit parameters](../../related-work/implicit-parameters.md),
  [traits without coherence](../../related-work/traits-without-coherence.md), which takes this draft's
  Cairo material, and [Rust's own proposals](../../related-work/rust-language-proposals.md), which
  covers the proposals and draws on this draft's context-as-dictionary framing and limitations.
- **Strategy:** the deep-dive playbook in [formats.md](../../communication-strategy/formats.md), not
  the release-announcement guide, and the comparison-piece rule that each compared design is shown as
  its authors would recognize it; the conversation is recorded in
  [evidence.md](../../communication-strategy/evidence.md#the-conversations-that-draw-attention).

**Context shapes.** The primer's `Hash` example wires a value context, `Person`, to a self-targeted
component. From the fully incoherent `Serialize<T>` on, the post moves the value into a parameter and makes
the context environmental, saying so where it happens; the `Name`, `Clone`, arena, and `Greet` examples use
environmental contexts, and `App` is an application context, per
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target).

## What it needs before publication

- **The documents it links.** The related-work paragraph links the *Traits without coherence*
  comparison, which sits on `incoherent-rust` with the revised *Rust's own proposals* and merges with
  the post.
- **The concessions survive.** The limitations and what-CGP-does-not-solve sections are the most
  valuable content for this audience, which is mapping the boundary.
- **Publication mechanics.** The front matter has only `authors: [soares]`: it needs an explicit `slug`,
  a `tags` entry, `deepdive`, and a written `description`. The `<!--truncate-->` marker is in place. The conventions are in [README.md](README.md#publication-conventions).
- **The nightly crate merges with it.** `example-code-nightly` and its CI job in `test-deploy.yaml` exist only
  on the post's branch, so the merge into `main` carries them, and
  [site.md](../site.md#the-example-code-crate) then describes the crate beside `example-code`.
- **A last currency check** of the discussion before publication, since the project goal and the
  authors' blogs may move again.

The post's CGP snippets compile in the website's
[`example-code/tests/blog/incoherent_rust_today.rs`](https://github.com/contextgeneric/contextgeneric.dev/blob/main/example-code/tests/blog/incoherent_rust_today.rs).
The four sections that use the `Name` component keep Boxy's associated constant, whose `RealName`
calls `core::any::type_name` and so needs nightly's `const_type_name` feature; the post says so, and
they compile in
[`example-code-nightly/tests/blog/incoherent_rust_today.rs`](https://github.com/contextgeneric/contextgeneric.dev/blob/main/example-code-nightly/tests/blog/incoherent_rust_today.rs),
with the rejected struct-binding snippet as a compile-fail fixture there.

## Maintaining it

Until it publishes, revise it freely, argument included. Once published, it is a dated artifact under
the [prohibition on rewriting](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts), which matters more here because a
post about a live discussion dates fast; record the drift here instead. Record here too if the upstream
design work adopts, rejects, or supersedes any of its arguments, since that changes what the project
should say next.
