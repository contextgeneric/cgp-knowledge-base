# Formats: per-artifact playbooks and worked drafts

This document turns the audience model and the message into per-artifact instructions: for each kind
of public writing — a launch post, a blog deep-dive, a README, a talk, a thread, a comparison — the
opening move, the length, the dismissal to preempt, and the next step to ask for. It ends with
annotated model drafts, so a writer can watch the whole apparatus operate on finished copy rather than
re-derive it from rules.

Two artifacts are governed elsewhere because they earned their own guides. The **website homepage** is
[../website/writing-guides/homepage.md](../website/writing-guides/homepage.md) and the **website
tutorials** are [../website/writing-guides/tutorial.md](../website/writing-guides/tutorial.md); the
playbooks below cover a project README and a blog deep-dive, which are their nearest cousins, and
defer to the guides where they overlap.

## Deciding in order

A piece is shaped by its format as much as by its message, so the decisions are made in a fixed order:
**channel → reader → voice → format → hook.** [evidence.md](evidence.md) says where the audience
gathers and what earns its attention; [readers.md](readers.md) says who is reading;
[voice-and-register.md](voice-and-register.md) says whether this surface speaks as the project or as
the author; and this document says how to structure the artifact once those are settled. Skipping the
order is how a piece ends up written for no one, in a form its channel punishes, in a voice that does
not match the surface it appears on.

Every playbook below shares four moving parts, named once so the entries stay short. The **opening
move** is the first thing the reader meets and the only thing a skimmer may read, so it carries a
concrete pain or a runnable example, never the paradigm. The **length and depth** are set by the
channel's patience and the reader's place on the
[prerequisite ladder](readers.md#the-comprehension-barriers). The **dismissal to preempt** is the
reflex that audience fires first — "verbose", "just macros", "another DI framework", "the name says
nothing" — which must be defused in the opening lines, because it is answered upstream or not at all.
And the **next step** is the single ask, matched to what that reader is ready to do.

## The link-aggregator launch post

This is where CGP is actually discussed, so it is the format to get right first, and its reader is the
pragmatic skimmer who will form and broadcast a snap judgment. It runs in the **author voice**, since
these submissions are posted by a person and answered by them in the thread.

Title it with the concrete-capability half of the tag line rather than the paradigm name —
"pluggable trait implementations for Rust, at compile-time" over "context-generic programming" —
because the title is the whole pitch for most of the audience. Open the body on a runnable example or
a short before/after from [message.md](message.md); the one piece of feedback CGP's own launch
received asked for exactly this ([evidence.md](evidence.md)). Keep the post short and let the linked
material carry depth. Preempt the two dismissals this audience fires fastest — "over-engineered" and
"why not just traits" — in the first paragraph, by naming the pain that justifies the machinery and
conceding where a plain trait suffices. Then be present in the thread: this channel expects the author
to answer, and the ready responses below are what to keep at hand. The ask is the quickstart, not the
paradigm.

## The blog deep-dive

A deep-dive has the reader's sustained attention and is the format the author's voice was made for, so
it runs first-person and can run long — the Hypershell post is roughly 16,500 words. The rule that
makes length work is to **declare it up front**: an estimated reading time and a paragraph-per-section
preview, so the reader knows what they are committing to and can navigate rather than abandon.

Open on a concrete problem the reader already has, never on the consumer/provider split or coherence.
Lead with the vanilla-looking idioms so early code reads like ordinary Rust, and reveal machinery only
when a reader has a reason to want it. Carry **one running example the whole way through** rather than
switching per concept, so understanding compounds — this is what let a forty-minute talk and a
16,500-word post each stay concrete. Set the error-message expectation honestly before the reader hits
one. And where the post has a costs section, write it at length and in the author's register: name
what is slow, what is missing, and what you do not yet understand about why.

## The README and project front matter

A README's job is the first screen, where an evaluator and a skimmer both decide in seconds. It runs
in the **project voice**. Put the tag line at the top beneath the project name, with a reassurance
line under it that heads off the runtime-container and new-language misreadings, then the curated
headline set from [identity.md](identity.md), then code above the fold, because a reader wants to see
code before prose. State "a library on stable Rust" and the install line early, since the evaluator is
scanning for the toolchain gamble. Keep the feature set to the ruthless few. The asks are the
quickstart for the skimmer and the honest maturity discussion for the evaluator. The
[homepage guide](../website/writing-guides/homepage.md) works the same layout out in more detail and
should be read alongside this entry, since the two surfaces share a job.

## The conference talk or video

A talk has the most room to motivate, and its audience forgives depth if the *why* comes first. It
runs in the **author voice**, including the self-introduction. Open on the problem, spend the middle on
a single idea, and defer the theory to a late section for the audience that stayed. Show
vanilla-looking code first and machinery only after the value has landed. Close on honest limits.

CGP has now given one such talk, and the next should be built from it rather than from this paragraph.
The [RustLab 2025 transcript](../website/blog/rustlab-2025-coherence.md) follows this structure
closely — it builds the coherence problem sympathetically before working around it, exhausts the
existing workarounds, states its thesis in one line, demonstrates on `cgp-serde`, and closes on the
learning curve and the error messages. Two moves generalize. **Grounding the whole argument in one
universally-known library**, rather than an invented example, is what let forty minutes stay concrete.
And **publishing the transcript with the slides inline and the video embedded** turns a talk into
indexable, linkable, quotable material for the far larger audience that will never watch it; treat
that as part of the format rather than an afterthought.

## The social thread

A thread has seconds of attention and one job: earn the click without inviting the dunk. Lead with one
concrete pain or one striking before/after, keep jargon out of the first post entirely, and let a
single link carry the depth. Do not open on the paradigm name, and do not compress the pitch so far
that it reads as an overclaim — the skimmer who feels oversold broadcasts that reaction. This is a
hook-delivery mechanism, not a place to explain.

## The comparison or positioning piece

A comparison earns disproportionate trust when it is honest and does disproportionate damage when it
is not, so its rule is non-negotiable: **never disparage the compared tool, and name where it is
simply the better choice.** Represent every alternative as its own users would recognize it, drawing
the sentiment from the [related-work](../related-work/README.md) documents and the judgment from
[message.md](message.md#when-not-to-reach-for-cgp). A comparison table works well here provided each
row concedes the case where the other tool wins; a table showing CGP winning every row reads as a
strawman and loses the reader it most wanted. The ask is the honest decision guide, not a verdict.

This format suits the author's voice particularly well, because his instinct on related work is
already to explain the other thing properly and to warn against flattering equivalences — "our
approach differs enough from tagless final that I want to avoid people thinking they're identical" is
the register to aim for.

## Answering in threads

Replying is its own format, and because the general channels expect the author present, a small set of
ready answers is worth keeping — each conceding the real cost before making the point, in the wording
[message.md](message.md#the-objections-readers-bring) fixes.

- **"Isn't this just a DI framework / macros / over-engineering?"** Concede that Rust needs no DI
  *framework* and that CGP is not one, then locate the concrete case plain traits handle awkwardly:
  overlapping impls the compiler rejects, an orphan-rule escape, a leaked-internals fix.
- **"How do I tell what code actually runs?"** Concede the indirection, then point at the wiring table
  as the one greppable place naming the provider for each component.
- **"What about compile times / the error messages?"** Concede both directions honestly, decline to
  invent a number, and name `check_components!` and `cargo cgp check` as the real mitigations.
- **"Why not just use traits?"** Agree that for one implementation, or a closed set, the plain tool
  wins, and point at the [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md).

## The conversion ladder

Every format ends by asking for a next step, and the right step depends on the reader rather than on
the piece. The **first-contact skimmer** is ready only for a low-commitment look — the quickstart, a
runnable example, the repository. The **working developer** is ready to try CGP on a real problem, so
point them at the pain narrative closest to theirs and the tutorial that walks it. The **evaluator** is
deciding on risk, so offer the honest maturity discussion, the incremental-adoption story, and a real
system built with CGP as social proof. The **enthusiast** is ready to go deep, so hand them the
[CGP Patterns book](https://patterns.contextgeneric.dev/) and the contribution path. Asking a reader
for more than their rung is ready for is how a piece that earned attention loses the conversion.

## Worked model drafts

The drafts below are the section's guidance assembled into finished copy, each followed by a note
tracing every move to the rule behind it. Read each draft first as a reader would, then read the
annotations to see the machinery. The point is not to copy the copy but to watch the apparatus
operate, so you can run it yourself.

Two caveats travel with every draft. They are illustrations rather than approved copy: adapting one
means re-running the decisions for the channel's reader, above all swapping in the pain that reader
feels most sharply. And every CGP claim and snippet is bound by the
[synchronization rule](../AGENTS.md#the-synchronization-rule) — verify against the source and the
`/cgp` skill before shipping, because a stale claim in a model draft is copied straight into real copy.

### A link-aggregator launch post

> **Pluggable trait implementations for Rust, at compile-time**
>
> Rust forbids two blanket impls that could ever overlap. That rule is right — it is what lets the
> compiler resolve a `where` clause you never wrote — but it means you cannot write both of these,
> even for a trait you own:
>
> ```rust
> pub trait CanEncode {
>     fn encode(&self) -> Vec<u8>;
> }
>
> impl<T: Display> CanEncode for T { /* ... */ }
> impl<T: AsRef<[u8]>> CanEncode for T { /* ... */ }   // error[E0119]
> ```
>
> `String` satisfies both bounds, so the compiler has no principled way to choose. The usual escape is
> a newtype wrapper per case, or a marker struct plus a helper trait — three extra lines of plumbing
> that several people have independently reinvented.
>
> CGP is that pattern, made a first-class thing. The value moves out of `Self` into a parameter, and
> each implementation targets its own zero-sized name, so both compile:
>
> ```rust
> #[cgp_component(Encoder)]
> pub trait CanEncode<Value> {
>     fn encode(&self, value: &Value) -> Vec<u8>;
> }
>
> #[cgp_impl(new EncodeWithDisplay)]
> impl<Value> Encoder<Value> where Value: Display { /* ... */ }
>
> #[cgp_impl(new EncodeBytes)]
> impl<Value> Encoder<Value> where Value: AsRef<[u8]> { /* ... */ }
> ```
>
> and each application says which one it uses, per type, in lines you can grep for:
>
> ```rust
> delegate_components! {
>     ApiServer {
>         open EncoderComponent;
>         @EncoderComponent.Uuid: EncodeWithDisplay,
>     }
> }
>
> delegate_components! {
>     Firmware {
>         open EncoderComponent;
>         @EncoderComponent.Uuid: EncodeBytes,
>     }
> }
> ```
>
> Coherence is not repealed — it is scoped. Overlapping providers coexist globally, and each context
> names exactly one, so `ApiServer` and `Firmware` encode the same `Uuid` differently without
> conflict. Everything resolves at compile time and compiles to a direct call: no trait objects, no
> runtime container, and nothing in the binary for a provider you don't use.
>
> To be clear about the cost: this is more machinery than a single trait needs. If a capability has
> one implementation, use a plain trait — CGP would be over-engineering. It earns its keep when the
> implementations genuinely multiply, when the choice must differ per context, or when the orphan rule
> is blocking you.
>
> It's a library on stable Rust and a superset of ordinary traits, so you can use it in one module and
> leave everything else unchanged.
>
> Quickstart: [link]

**The moves.** The title is the concrete-capability half of the [tag line](identity.md), not the
paradigm name. It opens on **the thing Rust rejects**, which is harder to answer with "just use a
trait" than the mock-in-tests pain is, and it **explains why the rule is right before working around
it** — the enhances-not-replaces frame and the author's characteristic move.

Two accuracy choices in the code are worth copying. The "before" uses a **trait the snippet itself
defines**, so the failure shown is unambiguously the overlap rule (`E0119`) — writing
`impl<T: Display> serde::Serialize for T` would have been an orphan-rule failure (`E0210`) that fails
on its own, and mislabelling it invites a correction in the first reply. And the shape change between
the two snippets — the value moving out of `Self` into a parameter — is **narrated rather than
smuggled**, because a reader comparing two versions of one program reads any unexplained difference as
sleight of hand. That move is the climb from rung 3 to rung 4 of the
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md), and it is what also dissolves the
orphan rule, which is why the closing paragraph can name it as a case CGP unblocks. The hand-rolled
workaround is named so the CGP version arrives as relief and the reader recognizes their own code
([evidence.md](evidence.md)). "Coherence is not repealed — it is scoped" preempts the informed
objection in one sentence. The cost is conceded in plain words, drawing the boundary
[message.md](message.md#when-not-to-reach-for-cgp) draws. The zero-cost claim is stated concretely
rather than as "zero-cost abstraction". And the ask is the quickstart, which is all the skimmer's rung
supports.

It is as notable for what it avoids: no paradigm name in the opener, no "magic", no "automatically
resolves", no unqualified "DI framework" — each an entry on the [avoid list](vocabulary.md).

### A README above the fold

> **Context-Generic Programming**
>
> *A language extension for Rust, with pluggable trait implementations at compile-time.*
>
> Still ordinary Rust — no nightly, no fork, no runtime cost. `cargo add cgp`
>
> ---
>
> **One Interface, Many Implementations.** Write many interchangeable implementations of the same
> interface and choose between them per context, with the overlapping and orphan implementations Rust
> normally forbids made safe because every choice is explicit and local.
>
> **Zero-Cost Abstraction.** Everything is resolved at compile time and compiles down to direct calls,
> so the flexibility costs nothing at runtime and unused providers never reach the binary.
>
> **Still Ordinary Rust.** A superset of ordinary traits you adopt one piece at a time: providers read
> like normal impls and implicit arguments like normal parameters, so a codebase can use it in one
> corner and stay otherwise vanilla.

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self) -> String;
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) -> String {
        format!("Hello, {name}!")
    }
}

#[derive(HasField)]
pub struct Person {
    pub name: String,
}

delegate_components! {
    Person {
        GreeterComponent: GreetHello,
    }
}

fn main() {
    let person = Person { name: "World".to_owned() };
    println!("{}", person.greet()); // Hello, World!
}
```

> **[Quickstart →]**  ·  **[Is it ready for production? — honest maturity notes →]**

**The moves.** The tag line is **layered**: the owned name as the title, the descriptor beneath, and a
reassurance line under that doing the skeptic's work before the reader supplies a worse reading of
"language extension". "A library on stable Rust" and the install line come early because the evaluator
is scanning for the toolchain gamble. Three of the five [headline features](identity.md) appear, each
title avoiding a repellent lead word and each sentence carrying its honest qualifier. Runnable code
sits above the fold, showing a component, a provider, an implicit argument, and wiring in the smallest
honest form — and it uses an `#[implicit]` argument rather than a getter trait, per the
[guides](../cgp/guides/reading-context-fields.md). There are two asks, matched to the two readers.

It deliberately omits a feature titled "Dependency Injection", which on a general front page imports
the runtime-framework baggage catalogued in [message.md](message.md#the-objections-readers-bring).

### A social thread

> **1/** Rust won't let you write two blanket impls that could overlap — not even for a trait you own.
> One impl for every `T: Display` and one for every `T: AsRef<[u8]>` can't coexist, because `String`
> matches both. The rule is correct. It's also, sometimes, exactly what you need to break. 🧵

> **2/** CGP lets both compile, by giving each implementation its own zero-sized name instead of
> implementing the foreign trait directly. Your app then picks one in a single line you can grep for.
> Two different apps can pick differently. No trait objects, no runtime dispatch — it compiles to a
> direct call.

> **3/** It's a library on stable Rust and a superset of ordinary traits, so you can try it in one
> module without rewriting anything. And if a capability has just one implementation, keep using a
> plain trait — this earns its keep once they multiply. [link]

**The moves.** The first post is one concrete constraint with no paradigm name, and it **grants that
the rule is correct** in the same breath, which is what stops the thread reading as a complaint about
Rust. The mechanism in post 2 is stated precisely rather than hyped — "compiles to a direct call" is
the [approved phrasing](vocabulary.md), chosen over "blazingly fast". Conceding "keep using a plain
trait" in the last post is what disarms the over-engineered reflex; a thread that only sells is the one
a technical crowd piles onto. One link carries the depth, and it is the whole ask.

### Adapting these

These are templates for the moves, not the words. Start by naming the dominant [reader](readers.md)
for your channel, then swap the anchor pain for the one that reader feels most sharply — the
orphan-rule escape for the trait-heavy developer, the error-type swap for the systems reader, the
monolith decomposition for the evaluator — because the pain, not the tag line, decides whether the
piece lands.

Three things must survive every adaptation. Keep the **conceded cost**; it is load-bearing rather than
optional politeness. Keep the **sympathetic account of what Rust already does**, since that is the
project's frame and its author's habit. And **re-verify every claim and snippet** against the source
and the `/cgp` skill before publishing. When you find a move these drafts do not cover — a talk opener,
a comparison table, a *This Week in Rust* blurb — the right next step is a new draft here, in the same
shape, so this grows into the section's library of worked models.
