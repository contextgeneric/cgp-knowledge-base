# Using an incoherent, dictionary-passing style Rust today

An unpublished post of about 12,800 words reading CGP against the Rust language-design discussion of
dictionary-passing style, incoherent traits, and context and capabilities, and arguing that CGP is a
working implementation strategy for a substantial fragment of those designs, on stable Rust today at a
stated cost.

- **URL**: none; the post is not published
- **Source**: `blog/2026-03-30-incoherent-rust-today.md` on the `incoherent-rust` branch of the
  [website repository](https://github.com/contextgeneric/contextgeneric.dev), not on `main`
- **Date in filename**: 2026-03-30, when the draft was written, not a publication date
- **Status**: Draft
- **Publication**: held until after the v0.8.0 release, so it does not compete with the
  announcement

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
  the author may be missing context: Nadrieril's posts on elaborating traits to dictionary-passing
  style and on traits carrying values, Boxy's *An Incoherent Rust*, and Tyler Mandry's
  context-and-capabilities work, read as one conversation with two separable goals, formalizing the
  trait system and building features on it. The post coins **TIR** (a traitless intermediate
  representation) and **Incoherent Rust** (the envisioned language), and analyzes the goals
  separately so one's feasibility does not decide the other.
- **A CGP primer for compiler-team readers:** no analogies or progressive disclosure, straight to
  provider traits with an explicit context parameter. It separates the two levels of coherence bypass
  (overlap through the provider-trait indirection, orphans by moving the target into a parameter) and
  asks whether CGP "truly solves" the orphan problem rather than asserting it.
- **Incoherent Rust desugared into CGP**, feature by feature: incoherent traits, named impls,
  incoherent trait bounds, incoherent bounds in a struct, and impl-specific bindings. Its sharpest idea
  is that **the context type is the dictionary**, one top-level dictionary carrying the others, which
  makes dependency instantiation tractable and lets cyclic dependencies resolve. Context and
  capabilities is a special case, worked as an arena-allocating deserializer.
- **Limitations, which make the post credible:** a `&self` context cannot supply mutable or owned
  values without interior mutability, and all bindings are declared in one place, so the nested
  dynamically scoped bindings *scoped impls* envision have no CGP equivalent short of something like
  inheritance. Centralized bindings may be a virtue, being easier to reason about, but are conceded as
  a restriction.
- **Where CGP diverges from Incoherent Rust:** what CGP has that the proposals do not (named impls as
  first-class types, incoherent functions, zero-arity traits, abstract types, explicit context types),
  related work (Cairo, ML modules, Scala implicits), and a conclusion split into what CGP solves,
  partially solves, and does not solve.

**The conclusion's staging argument:** a full dictionary-passing TIR is research-level and may need
dependent types, so Incoherent Rust need not wait for it; a front-end desugaring into CGP-shaped code
could ship the surface language first and be replaced later. If these features land, parts of the CGP
library become unnecessary while its patterns stay valuable, and CGP never aimed to be a framework
developers depend on indefinitely.

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
  [implicit parameters](../../related-work/implicit-parameters.md), and
  [Rust's own proposals](../../related-work/rust-language-proposals.md), which covers the proposals and
  the Cairo material and draws on this draft's context-as-dictionary framing and limitations.
- **Strategy:** the deep-dive playbook in [formats.md](../../communication-strategy/formats.md), not
  the release-announcement guide, and the comparison-piece rule that each compared design is shown as
  its authors would recognize it; the conversation is recorded in
  [evidence.md](../../communication-strategy/evidence.md#the-conversations-that-draw-attention).

## What it needs before publication

- **A currency pass, the substantial item.** The draft was written days after the posts it answers.
  Re-read where the discussion now stands: a conversation that has moved on needs the post reframed,
  and newer material needs engaging. That is the difference between a contribution and a late reply,
  and the author's judgement, not an agent's.
- **The concessions survive, checked first.** The limitations and what-CGP-does-not-solve sections
  are the most valuable content for this audience, which is mapping the boundary; a revision that trims
  them removes the reason to read the post.
- **Publication mechanics.** The front matter has only `authors: [soares]`: it needs an explicit
  `slug` and a `tags` entry, `deepdive`. The `{/* truncate */}` marker is in place. The filename date
  becomes the publication date. The conventions are in [README.md](README.md#publication-conventions).
- **Every snippet verified against v0.8.0** and the modern idioms the
  [guides](../../cgp/guides/README.md) teach, since this audience scrutinizes the code most, and
  showing forms the project recommends against undermines a post arguing CGP is a viable strategy.
- **Decide whether the CGP primer stays.** It makes the post self-contained for a reader new to CGP,
  and the [explanation tier](../writing-guides/explanation.md) now exists to link instead. Keeping it:
  this audience wants precision the explanation pages do not carry, and will not follow a link out
  mid-argument. Cutting it: the rule, stated for the [Projects pages](../writing-guides/project.md),
  that a piece teaches its own subject only. The primer is short and pitched differently, so keeping
  it is probably right, but it should be a decision.

## Maintaining it

Until it publishes, revise it freely, argument included. Once published, it is a dated artifact under
the [prohibition on rewriting](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts), which matters more here because a
post about a live discussion dates fast; record the drift here instead. Record here too if the upstream
design work adopts, rejects, or supersedes any of its arguments, since that changes what the project
should say next.
