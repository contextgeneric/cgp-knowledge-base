# Identity: the tag line, the pitch, and the headline features

This document fixes what CGP says about itself in one line, in one paragraph, and in one screen — the
settled tag line, the pitch that must follow it, and the small curated feature set a front page
shows — and it opens with the positioning decisions all three follow from. The three are one artifact
at three lengths, which is why they are governed together: a feature title that contradicts the tag
line's frame does as much damage as a wrong tag line.

## The positioning, in the order it was decided

The tag line is the last thing positioning produces, not the first. Stating the decisions behind it in
order lets a writer defend the line rather than repeat it. Product-marketing practice
fixes that order as five questions, answered one after another: what a reader would use instead, what
CGP does that those alternatives cannot, what that is worth, who cares enough to act on it, and which
category makes the value obvious. The method is cited in
[evidence.md](evidence.md#sources-for-the-craft-this-section-borrows). CGP's answers are below, and
every later section of this document is a consequence of one of them.

- **What a reader uses instead.** A plain trait with one implementation, or a trait-bounded generic.
  An enum over a closed set of alternatives. `dyn Trait` when the set is open at runtime. A newtype
  wrapper to get past the orphan rule, or a hand-rolled marker struct plus a helper trait to let two
  blanket impls coexist. A dependency-injection crate. Waiting for a language feature. Each is the
  right tool somewhere, and [message.md](message.md#when-not-to-reach-for-cgp) says where.
- **What CGP does that they cannot.** Several overlapping implementations of one trait coexist, and
  each context names the one it uses. A trait gains an implementation for a type its author does not
  own, with no wrapper. A provider declares its dependencies on the implementation, so they never
  reach the interface callers see. A type such as the error type is chosen by the context rather
  than passed as a parameter through every layer. All of it resolves at compile time, on stable Rust,
  as a superset of ordinary traits.
- **What that is worth.** An implementation swapped per application with no runtime cost and one
  greppable line to read. The orphan rule escaped without a newtype. Signatures that stop growing as
  dependencies join. A core that names its runtime and error type abstractly and so stays
  `no_std`-friendly. The strengths are argued in
  [message.md](message.md#the-strengths-worth-advertising).
- **Who cares enough to act.** A working developer who has more than one implementation of an
  interface and is paying for it in `dyn`, generics, or feature flags. A library author extending
  types they do not own, or writing code generic over a type's structure. A maintainer whose call
  graph threads parameters no middle layer touches. The type-system reader who has wanted overlapping
  instances made safe. Who does not: a codebase with one implementation per trait, a small closed
  variant set, or a set of implementations known only at runtime. The profiles are in
  [readers.md](readers.md).
- **Which category makes the value obvious.** *A language extension for Rust.* "A dependency-injection
  framework" is accurate in substance and imports the runtime-container baggage this audience
  rejects. "A modular programming paradigm" is honest, undersold CGP for most of its life, and leads
  with a word that repels. "A language" or "a superset of Rust" overclaims, since CGP adds no grammar.
  "Type classes without the orphan rule" is right for the functional-programming reader and opaque to
  everyone else, so it is a channel-specific frame rather than the category. "Extension" carries
  the ambition, implies addition rather than replacement, and survives the reader most able to check
  it.

The line below follows from the last answer, its "pluggable" from the second, its "at compile-time"
from the third, and the [frame](#the-frame-the-whole-identity-serves-enhances-not-replaces) from the
fourth: a reader who already uses traits well is the reader CGP wants, and a claim to replace what
they use loses them.

## The tag line

CGP's lead descriptor is settled:

> **A language extension for Rust, with pluggable trait implementations at compile-time.**

This is the line to open with wherever a reader meets CGP for the first time — the front page, the
README, a talk, a post — and every other piece of public writing echoes it rather than reinventing
it. It is fixed for consistency's sake, but a tag line's real grade is empirical, so watch which
questions and dismissals it attracts in the channels where readers gather, per
[evidence.md](evidence.md), and treat a recurring misreading as data rather than noise.

## The frame the whole identity serves: enhances, not replaces

Before the words, the frame. **CGP extends Rust's trait system; it does not substitute for it**, and
every level of the identity — line, pitch, features — must reinforce that. This is not a defensive
hedge bolted onto a bolder claim; it is the accurate description and the one that earns this
audience. A Rust programmer who suspects a crate wants to replace the language's core abstraction
stops reading, while one who understands that a CGP trait is still a trait, that a consumer trait can
be implemented directly with no CGP machinery at all, and that a project can use CGP in one module
and stay otherwise vanilla, has no reason to feel threatened by any of the rest.

The frame reaches past the trait system, and the extra distance is worth spending because it answers a
fear the trait framing alone does not. The patterns a Rust developer already uses to absorb variation — a
generic parameter on a struct, an enum over the alternatives, a boxed trait object — are not things CGP
displaces; a context is free to hold any of them while wiring its components normally, which is what
stops the multiple-contexts idea from reading as a demand to separate every axis of a program. Say it as
composition: CGP decides which variations are worth their own type, and the reader's existing tools keep
handling the ones that are not. The worry this defuses, and the shape a real application lands on, are in
[message.md](message.md#the-objections-readers-bring).

The frame is also what makes the honesty easy. "A superset of ordinary traits", "a library on stable
Rust", and "adopt it one component at a time" are all true, all reassuring, and all reinforcing of
the same idea, so a writer never has to choose between accuracy and reassurance. And it sets the tone
the [voice guidance](voice-and-register.md) prescribes for the whole project: explain what Rust
already does, sympathetically and correctly, before showing what CGP adds.

## Why each word of the line is there

Each part of the line does one job the others cannot, which is why none can be dropped.

**"A language extension for Rust"** carries the ambition honestly. "Extension" says CGP meaningfully
enlarges what the language can express while implying *addition to* rather than *replacement of*, so
it supports gradual adoption instead of fighting it. It is also the defensible version of bolder
framings that were rejected: calling CGP "a language of its own" or "a superset of Rust" overclaims,
because CGP is a set of procedural macros that desugar to ordinary Rust and compile on stable — it
adds no grammar — and the precise, vocal part of the Rust audience will answer "it's not a language,
it's a macro library" and win that exchange. An embedded, macro-based DSL is fairly called a language
extension in ordinary usage, so the word keeps the ambition and stays honest.

**"Pluggable"** names the actual novelty, and it was chosen against two alternatives that miss.
It is not "reusable", because to a Rust developer traits already *are* the reuse mechanism — one
interface, many types — so "reusable trait implementations" describes something the reader believes
they already have and points at the wrong axis. It is not "swappable", which says the right thing but
reads as a coinage next to a term of art. "Pluggable" names the real novelty: one interface with
many interchangeable implementations, each chosen per context — the thing Rust's
[coherence rules and the orphan rule](../cgp/concepts/coherence.md) normally forbid.

**"Trait implementations"** grounds the abstraction in something the reader uses every day, tying the
broad "extension" framing to the trait system rather than leaving an abstraction to decode.

**"At compile-time"** does two jobs. It defuses the runtime-dependency-injection misreading that
"pluggable" invites — the hidden container, the startup configuration, the reflection cost — by
saying up front that the choice is resolved statically. And it creates the tension that *is* the
pitch in miniature: for a Rust reader "pluggable" normally implies `dyn Trait`, a vtable, a plugin
loaded at startup, so following it immediately with "at compile-time" says *plugin-style swapping,
resolved statically, at no runtime cost*.

The line makes one deliberate omission and carries one known debt. It does **not lead with the owned
name**, because a name is not a pitch and "context-generic programming" is opaque on first contact —
observed, not hypothetical, in CGP's own release discussions where readers said the phrase obscures
more than it conveys ([evidence.md](evidence.md)). And "trait implementations" is narrower than
"language extension" promises, saying nothing of the abstract types, extensible data, and handler
family that make CGP broad, so the line slightly undersells its own reach. That debt is paid by the
pitch below rather than by cramming more into the line.

### The predecessor, and the lesson it left

For most of the project's life CGP described itself as **"a modular programming paradigm for Rust."**
That line was honest and overclaimed nothing. Where it still appears on the live site is tracked in
the website section's [redesign queue](../website/redesign-queue.md). It underperformed for two
separable reasons. It **undersold what CGP had become**, hiding behind "a paradigm" the abstract
types, extensible data, handlers, and namespaces that had accumulated. And its **lead word repelled
part of the audience on contact**: "modularity" is not something a developer wakes up wanting,
"paradigm" reads as academic, and for a large slice of the audience "modular" carries active baggage
from runtime dependency-injection frameworks — the hidden dependencies, the configuration weight, the
"magic" documented in [dependency injection](../related-work/dependency-injection.md).

The standing lesson is to **retire "modular" as a lead word**. It survives only as a supporting
descriptor, and when it is used it must be immediately differentiated from its framework
connotations by the three properties that distinguish CGP from a runtime container — compile-time,
zero-cost, and explicit.

## The pitch that follows the line

The tag line earns the next few seconds; the lines after it convert attention into understanding.
Build the pitch in the order below and stop wherever the format's patience runs out — a piece that
stops at the line alone leaves both the skeptic's first objection and the reader's "so what"
unanswered.

The first rung is the **reassurance subline**, which does the skeptic's work before the skeptic can:
*still ordinary Rust, on a stable toolchain, with no runtime cost, adopted one trait at a time*. It
heads off the two misreadings the line is most prone to — that "language extension" means a new
language to learn, and that "pluggable" means a runtime framework — and it is where the
enhances-not-replaces frame becomes explicit.

The second rung is the **breadth line**, which repays the tag line's debt in one sentence: beyond
swappable trait implementations, CGP adds [abstract types](../cgp/concepts/abstract-types.md) a
context chooses for itself — so an error type or a runtime stops being a parameter every layer has to
carry — [extensible records](../cgp/concepts/extensible-records.md) and
[variants](../cgp/concepts/extensible-variants.md), and a family of
[composable handlers](../cgp/concepts/handlers.md). This turns "an extension for one thing" into "an
extension broad enough to earn the word" without weighing down the line.

The abstract-types clause carries a payoff rather than only the mechanism, and that is deliberate.
"A context chooses for itself" describes what the construct *is*, which interests a reader who already
wants a type swappable; the clause about parameters names what it *removes*, which is the half a reader
with a deep call graph feels. A generic parameter is an input the caller supplies, so it propagates
through every intermediate signature, while an abstract type is determined by the context and
propagates nowhere — the argument is developed in
[impl-side dependencies](../cgp/concepts/impl-side-dependencies.md#type-dependencies-and-why-they-need-no-parameter)
and sold in [message.md](message.md#the-strengths-worth-advertising).

The third rung, and the most persuasive, is a **concrete pain** the reader has already felt, stated
before any mechanism — the overlapping impls Rust rejects, the orphan-rule newtype dance, the trait
that grew into a monolith. These live in [message.md](message.md), and one of them, chosen for the
channel's dominant reader, should almost always precede the abstract description of what CGP *is*.

The final rungs introduce the **owned name** and the **call to action**. Only after a concrete
benefit has landed should a piece name the paradigm — "this is what we call *context-generic
programming*" — always beside a plain descriptor, so the name attaches to an understanding the reader
now holds. The call to action is then matched to the reader's stage, per [formats.md](formats.md):
never ask a reader who has known CGP for thirty seconds to bet a codebase on it.

One rule governs the whole sequence: **concede the cost somewhere in it**. CGP is more machinery than
a plain trait, and for a trait with a single implementation a plain trait is the better tool.
Saying so is what makes the rest believable, and it costs nothing because it is true.

## The headline feature set

A feature set is the identity at one screen's length: four to six titles, each with a sentence,
scannable in the seconds a visitor gives a landing page. Its constraint is not coverage but
ruthlessness — the full catalog of advertisable strengths lives in [message.md](message.md) and a
writer picks from it per piece, while this set is fixed, shown to everyone at once, and read as a
whole. **A list of ten reads as a list of none**, and a reader remembers three.

Three rules follow. Each feature is a title and one or two sentences, never a paragraph. There are
four to six of them, never more. And each must be one of the strongest, broadest, most honest
strengths — which means above all that a **title must not lead with a word that repels** and a
**sentence must not overclaim to the audience most able to check it**.

The five below are the set, ordered most-important first.

- **One Interface, Many Implementations** — *"Write many interchangeable implementations of the same
  interface and choose between them per application, with the overlapping and orphan implementations
  Rust normally forbids made safe because every choice is explicit and local."* This is CGP's core
  identity, naming the strength directly and grounding the
  [coherence](../cgp/concepts/coherence.md) advantage. It says **per application** rather than per
  context because a front page is first contact and "context" is the term that most reliably loses a
  reader who has not met it, per
  [vocabulary.md](vocabulary.md#qualifying-a-context-and-a-target); the substitution costs a little
  precision, since a context need not be a whole application, and buys a sentence a cold reader can
  parse without a definition.
- **Zero-Cost Abstraction** — *"Everything is resolved at compile time and compiles down to direct
  calls, so the flexibility costs nothing at runtime and unused providers never reach the binary."*
  The strongest broad reassurance for a Rust audience that
  [explicitly prizes runtime performance](evidence.md), using a recognized Rust term in the title
  while the sentence states the concrete mechanism.
- **Type-Safe Wiring** — *"All wiring is checked at compile time, so a missing dependency is a build
  error rather than a runtime failure — and it runs entirely in safe Rust, with no `dyn`, `Any`, or
  reflection."* The differentiator against both dependency-injection frameworks and dynamic dispatch,
  carrying the [`check_components!`](../cgp/reference/macros/check_components.md) guarantee.
- **Abstract Over Every Dependency** — *"Write core logic that names its error type, runtime, and I/O
  abstractly and let each context supply the concrete choice — which keeps the core `no_std`-friendly,
  from embedded systems and kernels to WebAssembly."* This speaks to the systems programmer, and its
  payoff is a core that runs anywhere.
- **Still Ordinary Rust** — *"CGP is a superset of ordinary traits that you adopt one piece at a
  time: providers read like normal impls and implicit arguments like normal parameters, so a codebase
  can use it in one corner and stay otherwise vanilla."* This is the enhances-not-replaces frame as a
  feature, and it defuses the biggest adoption fear, which no other entry addresses.

### What the set deliberately leaves out

Two absences are choices rather than oversights. There is no feature titled **"Dependency
Injection"**, even though CGP is in substance compile-time dependency injection: on a general front
page that label imports the runtime-framework baggage catalogued in [message.md](message.md), so the
value ships through "Type-Safe Wiring" and "Abstract Over Every Dependency", and the explicit
"dependency injection, without the framework" pitch is reserved for channels where it lands. And
CGP's reach into specific domains — error handling, async runtimes, alternatives to dynamic dispatch,
decomposing large traits — stays out, because those are elaborations of the five above rather than
peers of them and belong in the longer material a reader reaches after the headlines have earned
their attention.

Where the live site departs from this set is recorded in the website section's
[redesign queue](../website/redesign-queue.md), and the
[homepage writing guide](../website/writing-guides/homepage.md) specifies where the set sits on the
page.

### Phrasing rules for feature titles

Titles obey the tag line's discipline compressed to four rules. Lead with the **concrete strength,
not an abstraction or a mechanism**. Avoid **"modular", "macros", and "magic"** as lead words, each
of which costs more attention than it wins. Use the **recognized Rust terms** — "zero-cost",
"type-safe", "no-std" — where they are accurate, since familiarity aids scanning. And write each
*sentence* to name a benefit and, wherever a skeptic would balk, the honest qualifier in the same
breath: "at compile time", "in safe Rust", "still ordinary Rust". The qualifier is what turns a claim
the reader would discount into one they believe.

One decision inside the set is worth recording with its reasoning, because it will look like an
omission otherwise. **"Abstract Over Every Dependency" pays off in portability rather than in
threading**, and that is deliberate. A `no_std`-friendly core running from embedded systems to
WebAssembly is the right claim for the systems programmer and is checkable in a way a claim about
signatures is not. The [breadth line](#the-pitch-that-follows-the-line) carries the *threading* payoff
instead — that an error type or a runtime stops being a parameter every layer has to declare — which
reaches a different and larger reader, someone whose signatures have filled up with types no
intermediate layer touches. Splitting them this way keeps the feature to a title and two sentences,
which is the set's own rule, and it puts each payoff where its reader is: a front page's job is the
snap category, and "fewer generic parameters" is a payoff a reader values only after they believe the
mechanism. The threading argument is made in full by the homepage essay's breadth section and the
Overview's feature tour, and the pain behind it is an entry in
[message.md](message.md#the-problems-cgp-removes).

## Keeping this document in sync

Because the tag line is settled, a change to it ripples across the section and must be propagated in
the same change. The line and its layered pitch appear as guidance in [formats.md](formats.md) and,
compressed, in [messaging-brief.md](messaging-brief.md); the
wording rules that justify it — retire "modular" as a lead word, prefer "extension", never ship the
name alone — are enforced in [vocabulary.md](vocabulary.md); the empirical caveat that publication is
the real measurement lives in [evidence.md](evidence.md); and the site surfaces the line touches are
listed in the [homepage guide](../website/writing-guides/homepage.md) and
[site-structure.md](../website/site-structure.md). When a feature's underlying behavior changes, the
[synchronization rule](../AGENTS.md#the-synchronization-rule) binds its sentence exactly as it binds
a reference document.
