# Vocabulary: the words about CGP, and the words of the craft

This document is the canonical word list, and it has two halves. The first governs the words used
*about CGP* in public — which term to use for each idea, which to defer until a reader is ready, and
which to avoid because it reliably creates a misreading. The second defines the words *of the craft*
— the marketing, public-communication, and developer-relations terms of art the rest of the section
uses — for a reader who is fluent in CGP and new to those disciplines. Both halves are lookups rather
than arguments, and this document is the authority the others defer to: when a phrasing rule here and
a rule elsewhere disagree, this one resolves it.

The scope is deliberately narrow. This document governs *which word*, not *what to pitch* (that is
[message.md](message.md)), not *how the prose should sound* (that is
[voice-and-register.md](voice-and-register.md)), and not *how CGP describes itself in one line* (that
is [identity.md](identity.md)).

## Terms to use, and how to introduce each

The established CGP vocabulary is the same in public writing as in the rest of the knowledge base, so
a reader moving between a blog post and the reference never reconciles two dialects. What public
writing adds is the gloss: introduce a term with a plain-language definition on first use, then use it
consistently.

- **Context** — the concrete type an application wires and calls methods on. Introduce it as "the type
  that owns the wiring — your application, your test harness, your service", not as a bare `Self`,
  because a cold reader has no reason to know the two coincide.
- **Component** — one capability, defined once, that can have many implementations. Introduce it as
  "an interface you can wire an implementation for", and reserve the detail that it is a consumer
  trait plus a provider trait for when the reader asks how it works.
- **Consumer trait** and **provider trait** — the trait you *call* and the trait you *implement*.
  Introduce the pair only when a piece goes past the surface; for an introductory audience, "the trait
  you use" and "the code that implements it" carry the idea without the vocabulary.
- **Provider** — a named, swappable implementation of a component. Introduce it as "one implementation
  you can choose"; avoid explaining that it is a zero-sized marker type until the reader is reading
  generated code.
- **Wiring** — choosing which provider implements each component for a context. Introduce it as "a
  small table that says which implementation to use", and lean on the table image, which is the single
  most load-bearing analogy in CGP writing.
- **Impl-side dependency** — a requirement a provider states in its own implementation rather than in
  the interface callers see. Introduce it as "the provider declares what it needs, and callers never
  see it", because the encapsulation benefit is the point and "impl-side" means nothing cold.
- **Pluggable trait implementations** — the lead descriptor for the core capability, from
  [identity.md](identity.md). Prefer "pluggable" as the novelty word and always pair it with "at
  compile-time", because the tension between the two is the pitch in miniature.
- **Context-generic programming** — the name of the paradigm, never the pitch. Introduce it only after
  a concrete capability has landed, always beside a plain descriptor.
- **`cargo-cgp`** — CGP's error toolchain. Refer to it as "cargo-cgp, CGP's error toolchain" and to
  its use as "running `cargo cgp check`". Introduce what it does as "a dedicated checker that leads
  with the root cause" — it un-hides the buried cause and names the missing field instead of printing
  a wall of generated types. Prefer the framing **readable, root-cause-first, dramatically better and
  actively improving**, and always concede in the same breath that it is a **v0.1.0-alpha** reshaping
  the core wiring errors but not yet every class.

## Terms to defer, and how to reveal them

Some accurate terms are barriers rather than vocabulary for a reader low on the
[prerequisite ladder](readers.md#the-comprehension-barriers), and leading with one loses them before
the value lands. Defer these and reveal each only when the reader has a reason to want it, matching
the depth to the profile so the advanced reader gets the real word immediately.

- **Coherence** and the **orphan rule** — the reason the consumer/provider split exists, but a theory
  the reader does not need in order to adopt CGP. Defer them behind the concrete pain and introduce
  them, when at all, *through* that pain. A piece should never open on coherence — with one deliberate
  exception, a talk or long-form essay whose whole subject is the coherence argument, where the
  [RustLab transcript](../website/blog/rustlab-2025-coherence.md) shows how to build it up
  sympathetically first.
- **Blanket implementation**, **monomorphization**, **higher-ranked trait bound**, **`PhantomData`** —
  the machinery under the ergonomic surface. Withhold from introductory material; when the
  runtime-cost question makes monomorphization worth naming, introduce it as "the compiler generates a
  direct call", not as jargon.
- **`DelegateComponent`**, **`IsProviderFor`**, the **type-level table** — the mechanism, not the
  model. Keep them out of a beginner's view and describe the table with the settings-map analogy;
  bring the real traits in only for a reader reading an expansion or a compiler error.

## Words and framings to avoid

A handful of words reliably create the misunderstandings the section spends its effort preventing.
The through-line is that vague or grand wording lets the reader supply the worst reading, while a
precise, smaller claim forecloses it and survives scrutiny — which, with this audience, persuades
*because* it survives.

- Avoid **"magic"**, even admiringly — this audience reads it as a warning. Say **"explicit"**, and
  point at the wiring table and the declared dependencies.
- Avoid **"automatically resolves", "finds", or "figures out"** the implementation — the single most
  common misframing, and the one that undercuts the coherence-freedom story. Say the provider is
  **"named explicitly, in one readable place"**.
- Avoid flatly calling CGP **"a DI framework", "a reflection system",** or **"an effect system"** —
  each makes the reader expect runtime behavior CGP does not have. Qualify each — **"compile-time,
  reflection-free dependency injection"**, **"compile-time structural reflection"**, **"the
  dynamic-binding fragment of effect handlers"** — and state the distinguishing limit in the same
  breath.
- Avoid implying **any runtime component**, even a fast one. Say the wiring is **"resolved at compile
  time and compiled to a direct call"**.
- Avoid **"zero-cost abstraction"** as a lead outside a feature title — it is accurate but worn. Prefer
  **"compiled to a direct call, with no vtable and nothing in the binary for a provider you don't
  use"**.
- Avoid **"blazingly fast"** and any unbenchmarked **"faster than"**. Say **"there is no runtime cost
  to compare"**, which is honest and stronger.
- Avoid **"no boilerplate"**. Say CGP **"moves the wiring into one readable place"**, because there is
  wiring and the reader will find it.
- Avoid **"replaces traits"** or **"a new language"**. Say **"a superset of ordinary traits"**, **"a
  library on stable Rust"**, and **"an extension"** — the
  [enhances-not-replaces frame](identity.md) is the project's core positioning, so this pair is more
  than a wording preference.
- Avoid **"reusable"** as the word for the novelty — to a Rust reader traits are already the reuse
  mechanism, so "reusable trait implementations" names nothing new. Say **"pluggable"**.
- Avoid **"just"** in a competitor's description — "just macros", "just another DI framework" are the
  reader's dismissals, not ours, and echoing them concedes the frame.
- Avoid overstating maturity — **"works on stable Rust today"** is true and worth saying, while
  **"production-proven at scale"** needs evidence the evaluator will notice is missing.
- Avoid calling CGP's errors **"solved", "fixed",** or **"now as clear as any other Rust error's"**.
  Say a dedicated checker **"leads with the root cause"** for the classes it recognizes, and concede
  the **v0.1.0-alpha**.

Sentence-level habits to avoid — adjective inflation, hedge stacking, corporate "we", invented
evidence — are a separate list and live in [voice-and-register.md](voice-and-register.md), because
they concern how the prose sounds rather than whether it is accurate.

## The name, and the community's bridge terms

The project's own name needs its own rule, because it is the term most likely to be misused as a
pitch. Never ship **"context-generic programming"** as a standalone hook: it is opaque on first
contact, and this is observed rather than hypothetical — readers in CGP's own release discussions said
the phrase obscures more than it conveys and reached instead for "structural typing" or "duck typing
for statically-typed code" to name what they thought it was ([evidence.md](evidence.md)). Always pair
the name with a plain descriptor, and treat those community-supplied phrases as *bridge terms* for
body copy — useful for meeting a reader where they are, but qualified, because CGP is nominal-and-wired
rather than truly structural and a precise reader will catch an unqualified "structural typing".

## The vocabulary of the craft

The rest of this document defines the non-technical terms of art the section uses, each anchored to an
intuition a systems programmer already holds, so a reader fluent in CGP and new to marketing never has
to guess what a word means. None of it is difficult or secret; it is a separate discipline with its
own words, and this is the word list. Treat each analogy as a handhold rather than an equation.

### The parts of a piece

Every piece of public writing is built from a small set of named parts, and naming them once is what
lets the playbooks in [formats.md](formats.md) stay short.

- **Hook** — the opening line whose only job is to make the reader read the next line. It is the fast
  path of a piece: nearly every reader hits it, most go no further, so if it is slow or unclear nothing
  downstream ever runs.
- **Tag line** — the compressed, one-line description of the whole project, usually the first thing a
  reader learns and sometimes the only thing. It is the project's `--help` summary line. CGP's is
  settled in [identity.md](identity.md).
- **Subline** — the second line beneath a hook or tag line, carrying the honest mechanism the hook left
  out. The hook earns the click; the subline heads off the reader's first objection before it forms.
- **Call to action (CTA)** — the single next step the piece asks for. Offer exactly one, the way a good
  CLI has one obvious default action: a reader handed five next steps takes none.
- **Above the fold** — what a reader sees before scrolling, borrowed from the top half of a folded
  newspaper. On a landing page it must carry the tag line and ideally runnable code, because many
  readers judge from it alone.

### Getting attention and choosing the category

- **Positioning** — the deliberate choice of the category a reader files you under, made before they
  choose a dismissive one ("oh, it's a DI framework"). A reader pattern-matches a new tool within
  seconds, so positioning is picking that match for them.
- **Framing** — the choice of angle and wording that decides how a reader reacts to a fact that is true
  either way. "Overlapping instances made safe" and "clever type-system trickery" describe the same
  feature; the frame is the message, not a decoration on it.
- **Value proposition** — the one-sentence answer to "what do I get, and why should I care?", stated as
  a benefit rather than a feature list. If a reader cannot state it after your opening, the call
  returned nothing.
- **Differentiation** — what CGP does that the obvious alternative cannot. A reader who sees no
  difference keeps what they have.

### Reaching people at scale, and sounding like one project

- **Channel** — where a piece appears: Lobsters, the Rust subreddit, a conference talk, a thread, the
  README. Each has its own audience, patience, and etiquette, so the channel is chosen before the
  words; [evidence.md](evidence.md) records where CGP's readers actually gather.
- **Curse of knowledge** — the expert's built-in inability to feel what a beginner does not yet know,
  which makes deep CGP fluency the biggest risk to explaining CGP well. It is the reason a compiler
  author writes the error message only they can read. It is answered construct by construct in
  [readers.md](readers.md#the-comprehension-barriers).
- **Message discipline** (or **one voice**) — using the same word for the same idea in every piece, so
  scattered posts reinforce one another. It is API stability for prose.
- **Clarity over completeness** — the rule that one idea a reader keeps beats five they forget. It
  fights the specification writer's instinct, where completeness is the virtue. Note the CGP-specific
  qualification in [voice-and-register.md](voice-and-register.md): this governs the *entry* to a piece,
  not its depth, since long-form depth is part of the project's voice.

### Earning and keeping trust

- **Social proof** — evidence from other people, especially peers and real running systems, that
  persuades where self-praise cannot. A developer believes another developer's working code far more
  than any adjective.
- **The funnel** (and **conversion**) — the staged path a reader travels from first hearing of CGP to
  advocating for it: heard-of, curious, trying, adopting, advocating. Readers drop out at every stage,
  and a conversion is one reader taking the next step. Each stage wants a different call to action —
  the conversion ladder the [formats.md](formats.md) playbooks end on.
- **Show, don't tell** — demonstrate a capability with running code rather than assert it with an
  adjective, because this audience trusts what it can run.
- **The pile-on** (and **dunking**) — a public group dismissal, where a technical community turns on a
  post it reads as arrogant or dishonest. The defence is the same as the honest move: claim only what
  is true, and never disparage another tool to elevate CGP.

## Keeping the list in sync

Because this document consolidates wording rules the others also apply, the coupling runs both ways.
When a rule changes here, check the phrasings in [message.md](message.md), the feature titles in
[identity.md](identity.md), and the register list in
[voice-and-register.md](voice-and-register.md), because a writer told to prefer a phrase in one place
must never be warned against it in another. When a CGP construct is renamed or a capability changes,
the terms here are bound by the [synchronization rule](../AGENTS.md#the-synchronization-rule) exactly
as a reference document is. And when you meet a term of the craft that is not defined above, add it in
the same change and in the same shape — a plain definition and a programmer's anchor — so this stays
the section's single home for the vocabulary.
