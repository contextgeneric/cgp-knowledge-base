# How to stop fighting with coherence and start writing context-generic trait impls — RustLab 2025 transcript

The full slide-by-slide transcript of CGP's first conference talk, delivered at RustLab 2025 in
Florence, with the slide images and a link to the recording. It is the clearest narrative the project
has published on why coherence exists, why the obvious workarounds fall short, and how provider traits
get around it — and because it is a talk transcript, it is almost entirely free of the syntax drift
that dates the release notes.

- **URL** — <https://contextgeneric.dev/blog/rustlab-2025-coherence>
- **Source** — [blog/2026-03-07-rustlab-2025-coherence/index.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-03-07-rustlab-2025-coherence/index.md)
- **Published** — 7 March 2026, untagged; carries 67 slide images and a
  [PDF of the deck](https://contextgeneric.dev/blog/rustlab-2025-coherence/cgp-rustlab-2025-slides.pdf)
- **Recording** — <https://www.youtube.com/watch?v=gXIfP-W9074>
- **Status** — Historical

## What it covers

The talk runs in three movements, and the shape is worth studying independently of the content because
it is the format's playbook executed well.

The first movement builds up **why coherence exists** before criticizing it. Traits plus generics give
Rust dependency injection for free — an impl can require `where Name: Display` without the caller
naming it, and the compiler resolves that and every transitive dependency by global lookup — and for
that to be sound, every lookup must find the same implementation. The overlap and orphan rules follow.
The talk then makes the case concrete with the **hash table problem**: a blanket `Hash` for any
`T: Display` conflicts with the specialized `Hash for u32`, and the reason "just prefer the specialized
impl" fails is that generic code can bind the blanket impl through a bound that never mentions `Hash`
at all, so by the time the type is known the specialization is invisible — and the chain of generic
callers can be arbitrarily deep. This is the sharpest published statement of *why* specialization does
not simply solve the problem.

The second movement walks the **existing workarounds**. Specialization is unstable, has known
soundness problems, and even if stabilized would not permit equally-general overlapping impls nor
touch the orphan rule. Serde's `remote` derive works but requires each library to write its own proc
macro. The talk then generalizes the remote pattern: if all those ad-hoc `serialize` functions share a
signature, classify them with a trait — a **provider trait** — that moves `Self` to an explicit
parameter, so the `Self` position becomes an *identifier naming an implementation*. Higher-order
providers follow for composing them, and then the problem of passing them around implicitly, which the
talk connects to the [context-and-capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)
proposal.

The pivot slide states the thesis in one line: *when writing implementations we want no coherence, and
when using them we want many local scopes each coherent within itself.* Provider traits deliver the
first, and an explicit context type delivers the second.

The third movement introduces CGP proper and demonstrates it with `cgp-serde`: `#[cgp_component]`,
`#[cgp_impl]`, `delegate_components!`, and a two-application demo where the same encrypted-message
archive serializes to different JSON. It closes by returning to the hash table problem to show CGP's
answer, giving an onboarding path, previewing DSLs and extensible data types, and — importantly —
naming the challenges: verbose error messages, a steep learning curve, and a young ecosystem. It
credits Edward Kmett's talk
[*Typeclasses vs the World*](https://www.youtube.com/watch?v=hIZxTQP1ifo) as a core inspiration.

## How it relates to the knowledge base

The talk's central argument is [coherence](../../cgp/concepts/coherence.md), and its
incoherence-then-local-coherence framing is the same one that concept document is built on; the talk
is the more narrative telling of it. The trait split is
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), the free
dependency injection it opens with is
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md), the composition step is
[higher-order providers](../../cgp/concepts/higher-order-providers.md), and the demo is the
[modular serialization example](../../examples/modular-serialization.md) with
[cgp-serde](../../projects/cgp-serde/README.md) behind it.

Its comparisons map onto the related-work section: specialization and the overlap rule to
[type-classes](../../related-work/type-classes.md), the capability-passing proposal to
[implicit-parameters](../../related-work/implicit-parameters.md), and the Kmett talk to the
type-class lineage CGP descends from.

For the communication strategy this post is the single most useful artifact on the site. It is
**evidence that the conference-talk channel works** — the format playbook in
[formats.md](../../communication-strategy/formats.md) was written for a talk that had not yet
happened, and this is one that has, structured almost exactly as that playbook prescribes: motivation
first, one central "aha," theory deferred, honest limits at the close. Its discussion threads on
[Reddit](https://www.reddit.com/r/rust/comments/1rn9vii/how_to_stop_fighting_with_coherence_and_start/),
[Lobsters](https://lobste.rs/s/jreugl/how_stop_fighting_with_coherence_start), and
[Hacker News](https://news.ycombinator.com/item?id=47287502) are reception evidence for
[attention-and-engagement.md](../../communication-strategy/attention-and-engagement.md). And
publishing the transcript as a blog post — with slides inline and the video embedded — is a reusable
pattern that turns an ephemeral talk into indexable, linkable, quotable material.

## Where it diverges from CGP v0.8.0

Very little, because the talk shows only a handful of small snippets and spends its code budget on
*vanilla* Rust illustrating the problem rather than on CGP illustrating the solution.

- **The `cgp-serde` wiring uses `UseDelegate` with a nested table**, the legacy dispatch form; the
  current idiom is the `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **The debugging advice recommends LLMs.** Slide 63 names large language models as the practical way
  to decipher CGP's error messages, and says compiler changes would be needed in the long term.
  [`cargo-cgp`](../../cargo-cgp/README.md) had not been released; it is now the first thing to reach
  for, and any restaging of this talk should say so.
- **CGP is described as "a modular programming paradigm."** That is the retired framing;
  [tag-lines.md](../../communication-strategy/tag-lines.md) fixes the current line as "a language
  extension for Rust, with pluggable trait implementations at compile-time."

## Maintaining it

Leave it alone — a transcript is a record of what was said, and editing it would misrepresent the
talk. If the talk is given again, the deck should be revised rather than this post, and a new
transcript published beside it.

The material worth reusing is substantial and mostly syntax-free. The hash-table walkthrough, and
specifically the argument for why preferring the specialized impl cannot work, is the best available
explanation of that point and belongs in any piece that must justify coherence before working around
it. The three-part structure — build the problem, exhaust the workarounds, then present the answer —
is the template for the next talk.
