# How to stop fighting with coherence and start writing context-generic trait impls - RustLab 2025 transcript

The slide-by-slide transcript of CGP's first conference talk, at RustLab 2025 in Florence, with the
slides and the recording. It is the clearest narrative the project has published on why coherence
exists, why the obvious workarounds fall short, and how provider traits get around it, and as a talk
it is almost free of the syntax drift that dates the release notes.

- **URL**: <https://contextgeneric.dev/blog/rustlab-2025-coherence>
- **Source**: [blog/2026-03-07-rustlab-2025-coherence/index.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-03-07-rustlab-2025-coherence/index.md)
- **Published**: 7 March 2026, untagged; carries 67 slide images and a
  [PDF of the deck](https://contextgeneric.dev/blog/rustlab-2025-coherence/cgp-rustlab-2025-slides.pdf)
- **Recording**: <https://www.youtube.com/watch?v=gXIfP-W9074>
- **Status**: Historical
- **Notice**: a note at the top of the post, written on the website's `v0.8.0` branch, links the [cgp-serde pages](https://contextgeneric.dev/docs/projects/cgp-serde/), including the two-application demo the talk ran live, and the *Coherence* Concepts page; it is the sanctioned edit in [../AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts) and changes no claim

## What it covers

Three movements, a template for the next talk: build the problem, exhaust the workarounds, then
present the answer.

- **Why coherence exists:** traits and generics give Rust dependency injection, since an impl can
  require `where Name: Display` and the compiler resolves it and every transitive dependency by global
  lookup; soundness needs every lookup to find the same implementation, hence the overlap and orphan
  rules. The **hash table problem** makes it concrete: a blanket `Hash` for `T: Display` conflicts with
  `Hash for u32`, and "prefer the specialized impl" fails because generic code can bind the blanket
  impl through a bound that never mentions `Hash`, through an arbitrarily deep chain of callers. This
  is the best available explanation of why specialization does not solve the problem, and belongs in
  any piece that must justify coherence before working around it.
- **The workarounds:** specialization is unstable, has soundness problems, and even stabilized would
  not permit equally general overlapping impls or touch the orphan rule. Serde's `remote` derive works
  but needs each library's own proc macro. Generalizing it, a **provider trait** classifies the ad-hoc
  `serialize` functions and moves `Self` to a parameter, so the `Self` position names an
  implementation; higher-order providers compose them, and passing them implicitly connects to the
  [context-and-capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)
  proposal. The pivot slide's thesis: *when writing implementations we want no coherence, and when
  using them we want many local scopes each coherent within itself*; provider traits give the first
  and an explicit context type the second.
- **CGP:** `#[cgp_component]`, `#[cgp_impl]`, `delegate_components!`, and a `cgp-serde` demo where
  one encrypted-message archive serializes to different JSON in two applications. It returns to the
  hash table problem with CGP's answer, gives an onboarding path, previews DSLs and extensible data
  types, and names the challenges: verbose error messages, a steep learning curve, and a young
  ecosystem. It credits Edward Kmett's
  [*Typeclasses vs the World*](https://www.youtube.com/watch?v=hIZxTQP1ifo) as an inspiration.

## How it relates to the knowledge base

- **Concepts:** [coherence](../../cgp/concepts/coherence.md), built on the same
  incoherence-then-local-coherence framing, which the talk tells as narrative;
  [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md);
  [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md) for the opening; and
  [higher-order providers](../../cgp/concepts/higher-order-providers.md). The demo is the
  [modular serialization example](../../examples/modular-serialization.md), with
  [cgp-serde](../../projects/cgp-serde/README.md) behind it.
- **Related work:** specialization and the overlap rule map to
  [type-classes](../../related-work/type-classes.md), the capability-passing proposal to
  [implicit-parameters](../../related-work/implicit-parameters.md), and the Kmett talk to the
  type-class lineage.
- **Strategy:** evidence that the conference-talk channel works, structured almost exactly as
  [formats.md](../../communication-strategy/formats.md)'s playbook prescribes (motivation first, one
  central insight, theory deferred, honest limits at the close); its reception is in
  [evidence.md](../../communication-strategy/evidence.md). Publishing a transcript with slides inline
  and the video embedded turns a talk into indexable, quotable material.

## Where it diverges from CGP v0.8.0

Very little: the talk's few snippets are mostly *vanilla* Rust illustrating the problem.

- **The `cgp-serde` wiring uses `UseDelegate` with a nested table**, the legacy dispatch form; the
  idiom is the `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **The debugging advice recommends LLMs.** Slide 63 names large language models as the practical
  way to decipher CGP's errors, with compiler changes needed long term.
  [`cargo-cgp`](../../cargo-cgp/README.md) had not been released; it is now the first thing to reach
  for, and a restaging should say so.
- **CGP is described as "a modular programming paradigm."** That framing is retired;
  [identity.md](../../communication-strategy/identity.md) fixes the line as "a language extension for
  Rust, with pluggable trait implementations at compile-time."

## Maintaining it

Leave it alone: a transcript records what was said. If the talk is given again, revise the deck and
publish a new transcript beside this one.
