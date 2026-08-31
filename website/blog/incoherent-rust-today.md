# Using an incoherent, dictionary-passing style Rust today

An unpublished post, roughly 12,800 words, that reads CGP against the Rust language-design discussion
of dictionary-passing style, incoherent traits, and context and capabilities, and argues that CGP is a
working implementation strategy for a substantial fragment of what those designs propose — available on
stable Rust today, at a stated cost.

- **URL** — not published
- **Source** — `blog/2026-03-30-incoherent-rust-today.md` on the `incoherent-rust` branch of the
  [website repository](https://github.com/contextgeneric/contextgeneric.dev), not on `main`
- **Date in filename** — 2026-03-30, which is when the draft was written rather than a publication date
- **Status** — Draft
- **Task** — B2 in [tasks.md](../tasks.md), held until after the v0.8.0 release

## Why this post is different from everything else on the blog

It is the only piece of CGP writing aimed at the
[language-design reader](../../communication-strategy/readers.md#the-language-design-and-compiler-team-reader),
and that reader is unreachable through the channels the rest of the blog is written for. Its audience
is compiler-team members and the people writing Rust's design posts on traits and coherence — readers
for whom nothing in CGP needs simplifying and for whom any imprecision is immediately visible. Every
other post argues that CGP is *useful*; this one argues that CGP is *evidence*, which is a different
and rarer kind of contribution.

It is also the only post whose value decays. The upstream discussion it answers is dated, so the
post's usefulness is a function of whether that conversation is still live — a property no release
note or deep dive has, and the reason its publication timing is a real decision rather than a
scheduling detail.

## What it covers

The post is built as an argument in five movements, and its length comes from taking each of them at
the precision its audience expects rather than from breadth.

It opens by **establishing the discussion it is joining**, deliberately as the author's own reading of
public material and with the caveat that he may be missing context. Nadrieril's posts on elaborating
Rust traits to dictionary-passing style and on traits carrying values, Boxy's *An Incoherent Rust*, and
Tyler Mandry's earlier context-and-capabilities work are treated as one conversation with two separable
goals: formalizing the trait system, and building higher-level features on top of that formalization.
The post coins two labels it then uses throughout — **TIR** for the hypothetical traitless intermediate
representation, and **Incoherent Rust** for the envisioned language — and insists the two objectives be
analyzed separately, so that the feasibility of one does not decide the other.

It then gives **a CGP primer written for compiler-team readers**, which is a register the site has
nowhere else: no analogies, no progressive disclosure, straight to provider traits with an explicit
context parameter. It distinguishes the two levels of coherence bypass — overlapping implementations
via the provider-trait indirection, and orphan implementations via moving the target into a parameter —
and asks directly whether CGP "truly solves" the orphan problem rather than asserting that it does.

The **central section desugars Incoherent Rust into CGP**, feature by feature: incoherent traits, named
impls, incoherent trait bounds, incoherent bounds inside a struct, and impl-specific bindings. It then
develops the post's sharpest idea, that **the context type is the dictionary** — a single top-level
dictionary carrying the others, which is what makes dependency instantiation tractable and lets cyclic
dependencies resolve. Context and capabilities is handled as a special case, with an arena-allocating
deserializer as the worked example.

It then spends real length on **limitations**, and this is the part that makes the post credible to its
audience. Two are named as fundamental to the single-context approach: a `&self` context cannot supply
mutable or owned values without interior mutability, and all bindings must be declared in one place, so
the nested dynamic-scoped bindings that *scoped impls* envision have no CGP equivalent short of
something resembling inheritance. The post argues the restriction may be a virtue — centralized
bindings are easier to reason about — while conceding it is a restriction.

A section on **where CGP diverges from Incoherent Rust** runs the comparison the other way, naming
things CGP has that the proposals do not: named impls as first-class types rather than a separate kind
of entity, incoherent functions, zero-arity traits, abstract types, and explicit context types. It
closes with related work — Cairo, ML modules, Scala implicits — and a conclusion split three ways into
what CGP solves, partially solves, and does not solve.

The conclusion's strongest move is its **staging argument**: that a full dictionary-passing TIR is a
research-level undertaking which may itself need dependent types, that Incoherent Rust should not have
to wait for it, and that a front-end desugaring into CGP-shaped code could ship the surface language
first and be replaced wholesale later. It ends by saying plainly that if these features land, much of
the CGP library becomes unnecessary — and that this was always the goal.

## How it relates to the knowledge base

The post's technical list is [coherence](../../cgp/concepts/coherence.md) and
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), with the two-level
bypass it describes corresponding to the tiers of the
[modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) — the provider-trait indirection
that legalizes overlap, and the move of the target into a parameter that dissolves the orphan rule. Its
context-as-dictionary framing is [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md)
stated for an audience that already knows what a dictionary is, and its capabilities section rests on
[implicit arguments](../../cgp/concepts/implicit-arguments.md) and
[`HasField`](../../cgp/reference/traits/has_field.md). The abstract-types divergence is
[abstract types](../../cgp/concepts/abstract-types.md); the arena example is the same scenario as the
deserialization half of [modular serialization](../../examples/modular-serialization.md).

Its related-work section overlaps [ML modules](../../related-work/ml-modules.md) and
[implicit parameters](../../related-work/implicit-parameters.md), and its Cairo material has no internal
counterpart — a related-work document on Cairo's trait-implementation model would be worth adding if
the comparison is kept.

On the strategy side it is governed by the deep-dive playbook in
[formats.md](../../communication-strategy/formats.md) rather than the release-announcement guide, and by
the comparison-piece rule that every compared design is represented as its own authors would recognize
it. The reader it serves is profiled in
[readers.md](../../communication-strategy/readers.md#the-language-design-and-compiler-team-reader), and
the conversation it attaches to is recorded in
[evidence.md](../../communication-strategy/evidence.md#the-conversations-that-draw-attention).

## What it needs before publication

**A currency pass is the substantial item.** The draft was written days after the posts it answers, and
that is no longer the situation. Re-read where the upstream discussion now stands before revising: a
conversation that has moved on needs the post reframed rather than merely finished, and one that has
produced newer material needs that material engaged. This is the difference between a contribution and
a late reply, and it is a judgement the author should make rather than an agent.

**The concessions must survive the revision, and should be checked first.** The limitations and the
what-CGP-does-not-solve sections are the post's most valuable content for this audience, because the
boundary is what a language designer is trying to map. A revision that tightens the post by trimming
them has removed the reason to read it.

**The publication mechanics are missing.** The front matter carries only `authors: [soares]`: it needs
an explicit `slug`, since without one Docusaurus publishes under a dated path, and a `tags` entry from
the fixed set — `deepdive` is the fit. The `{/* truncate */}` marker is already in place. The date in
the filename should become the real publication date. The conventions are in
[README.md](README.md#publication-conventions).

**Every snippet needs verifying against v0.8.0.** The draft predates the release the site is being
rebuilt around, and its CGP code is the most scrutinized this audience will ever read. It should also
be checked against the modern idioms the [guides](../../cgp/guides/README.md) teach, since a post
arguing that CGP is a viable implementation strategy is undermined by showing forms the project itself
recommends against.

**One structural question is worth settling deliberately:** whether the CGP primer stays. It exists
because the post must be self-contained for a reader who has never used CGP, and once the
[explanation tier](../writing-guides/explanation.md) exists there is somewhere to link instead. The
argument for keeping it is that this audience wants precision the explanation pages deliberately do not
carry, and that a compiler-team reader will not follow a link out mid-argument. The argument for
cutting it is the deep-dive rule that a piece teaches its own subject and nothing else. The primer is
short and pitched at a different level from the explanation pages, so keeping it is probably right —
but it should be a decision rather than an oversight.

## Maintaining it

Until it publishes this is a draft and the ordinary editing rules apply: revise it freely, including
its argument. The moment it publishes it becomes a dated artifact like every other post, and the
[prohibition on rewriting](../AGENTS.md#do-not-rewrite-history) applies — which matters more here than
usual, because a post about a live language-design discussion will date faster than a release note and
the temptation to keep it current will be correspondingly stronger. Record the drift here instead.

One thing to watch after publication: if the upstream design work adopts, rejects, or supersedes any of
the post's arguments, that is worth recording in this document, because it is the kind of reception
that changes what the project should say next rather than merely how a post landed.
