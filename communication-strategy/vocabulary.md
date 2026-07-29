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
  that owns the wiring", not as a bare `Self`, because a cold reader has no reason to know the two
  coincide. The word needs qualifying more often than any other term here; see
  [Qualifying a context and a target](#qualifying-a-context-and-a-target) below, which is the single
  most load-bearing wording rule in this document.
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

## Qualifying a context and a target

**"Context" is the most overloaded word in CGP's vocabulary, and unqualified use of it is the most
reliable way to lose a reader who was following.** The problem is not that the term is imprecise — it
means exactly the type in the `Self` position — but that the same word covers two situations a reader
experiences as opposites, and public writing moves between them without saying so.

Two qualifiers fix it, and both are needed because they answer independent questions.

- **Value context** — a context that *is* the data the capability operates on. The `String` in
  `String: CanEncode`, the `Rectangle` in `Rectangle: CanCalculateArea`. Introduce it as "here the type
  being encoded is also the type that carries the wiring — one type doing both jobs".
- **Environmental context** — a context that exists to supply choices and capabilities rather than to be
  operated on. Introduce it as "a type that stands for one set of choices", and say in the same breath
  that **it often has no fields at all** — `struct AppA;` is a complete context — because a reader
  meeting an empty struct with traits on it has no other way to guess what it is for. Use the qualifier
  where the contrast with a value context matters, and plain "context" in running prose once the reader
  knows which is in play.
- **Application context** — the typical environmental context, one standing for a whole application.
  Already the base's established compound, and the friendliest specific form.
- **Environment** — a simile, never a term. Spend it once on the readers whose prior model it matches —
  the Scala `given`, `Reader`-monad, and implicits audience — as
  [related-work does](../related-work/implicit-parameters.md): "CGP's context *is* their implicit
  environment, made a first-class, explicitly-wired type". Do not promote it: the paradigm is called
  *context*-generic programming, `__Context__` is what every diagnostic says, and "environment" leans
  runtime in a way [identity.md](identity.md) works hard to prevent.

A second, independent qualifier describes the **component** rather than its context.

- **Self-targeted** — the capability is about the `Self` type: `CanEncode`, `CanGreet`, `HasErrorType`,
  every getter.
- **Parameter-targeted** — the capability is about a type parameter while `Self` only decides:
  `CanEncodeValue<Value>`, `CanCalculateArea<Shape>`.

A parameter does not by itself make a component parameter-targeted. In `CanCompute<Code, Input>` the
target is `Input` while `Code` is a **selector** the wiring dispatches on, and a component may carry
both. The test is which type the capability acts on. Note also that the labels describe the *consumer*
trait: on the provider side both shapes carry the context (`Encoder<Context>` versus
`ValueSerializer<Context, Value>`), so the distinction is invisible in an expansion.

### Why the qualifiers are not jargon

Some readers will resist being taught three shapes where they expected one idea, and the answer to that
resistance is not to hide the distinctions but to show that **Rust already has them and simply never had
to name them.** Vanilla Rust idiomatically supports exactly one of the three: a value context whose
`Self` is the target. That is what `impl Display for String` is, and it is so dominant that a Rust
programmer has no reason to notice it *is* one option among several.

The other two shapes are legal in vanilla Rust and merely unrewarding. An environmental context works
until you try to share logic between two of them, at which point the blanket impls overlap. A
parameter-targeted trait on an application type compiles fine — `impl CanEncodeValue<Vec<u8>> for ApiServer`
alongside the same for `Firmware` genuinely gives per-application encoding, with no CGP involved — but
every context-and-type pair needs its own hand-written body and nothing can be factored out. So both
shapes exist and neither pays, which is why nobody carries them in their repertoire.

**That is the case to make: CGP's contribution is not legalizing these shapes but making their
implementations reusable, which is what turns each one into a technique.** Once all three are worth
using, a reader needs to be able to say which one they are in — so the qualifiers are the names of
choices that only became choices recently, not complexity CGP added. State it that way and the reader
stops hearing jargon and starts hearing an answer to "why three?". The
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) carries the full argument and the
use case for each shape.

### The confusions these qualifiers prevent

Four specific misreadings recur, and each is worth recognizing in a draft, because every one of them is
produced by *correct* prose that omitted a qualifier.

**"The context is `String`?"** A reader given the usual gloss — the type that owns the wiring, your
application — and then shown `String` as a context concludes they have misunderstood something. The fix
is not to avoid the word but to say once that at the retrofit shape the target and the context are the
same type, and that the fully modular shape separates them. Told forwards, the coincidence explains
itself; discovered by the reader, it reads as an inconsistency.

**"So a dedicated context is *less* general?"** Hearing "this provider works with any context" and then
"now we define a dedicated context" invites exactly the wrong inference. What widened is *who chooses*:
the choice moved from the type, which gets one, to you, who can define as many contexts as you like.
Say that explicitly rather than leaving the reader to infer a narrowing.

**Two examples on the same rung feeling like opposites.** `Person: CanGreet` and `String: CanEncode` are
both value contexts, and calling `Person` a context is unremarkable while calling `String` one is
jarring. A reader who forms their model on one and then meets the other loses it — so an introductory
example should say which shape it is rather than leaving the reader to generalize from a single case.

**The silent shift from data to application.** This is the worst of the four, because nothing signals
it: moving from `String: CanEncode` to a web application's `App: CanQueryUser` changes no signature and
adds no parameter, yet `Self` has stopped being data and become an environmental context. A piece that
crosses that line must say so in a sentence, or the reader simply notices at some point that they no
longer know what a context is.

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
- Avoid **coining a new term for a distinction the list above already names.** The recorded lesson is
  specific: readers said "context-generic programming" obscures more than it conveys, so a second or third
  coinage costs more attention than it wins, however well it compresses the idea for whoever coined it.
  When a piece needs to talk about whether a design absorbs variation into one type or separates it across
  several, the plain phrasings carry it with nothing to look up — **"a type standing for one set of
  choices"**, **"you already have two applications"**, **"which variations are worth their own type"**.
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
