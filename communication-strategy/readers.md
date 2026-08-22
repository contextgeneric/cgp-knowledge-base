# Readers: who they are, and what stops them understanding

This document is the audience model the rest of the section rests on. Its first half profiles the
readers public CGP writing must serve — what each already knows, what excites them, what makes them
skeptical. Its second half maps the comprehension barriers that stop a *willing* reader from
following, and the teaching moves that lower each one. The two halves are kept together because they
are two questions about the same person: **who is this for**, and **what will they fail to follow**.

## Naming the reader is the first decision in a piece

Public writing about CGP lands only when it is written for a definite reader, because CGP's ideas are
unfamiliar enough that one framing helps an audience while the same framing loses another.
"Overlapping instances made safe" reads as a gift to a Haskeller and as a warning to a pragmatic Rust
engineer that the crate is too clever. "No runtime container" reassures a systems programmer and
confuses a Spring developer who cannot picture dependency injection without one. Naming the reader
therefore comes before the outline and before the examples, because it decides which benefit to lead
with, how deep to go, which analogies to reach for, and which misunderstanding to head off first.

Two axes describe most readers and vary independently. The first is **how much Rust the reader
knows**, from someone a few months in to someone fluent in higher-ranked trait bounds. The second is
the **disposition** they bring: an enthusiast delighted by expressive type-level machinery, against a
pragmatist wary of complexity who distrusts clever code on sight. An expert can be either, and in the
Rust community the skeptic is both more common and harder to win, so writing that satisfies the
skeptic tends to satisfy everyone. A softer third axis is the **mental model imported** from another
language, which decides which analogies land; those backgrounds are covered in depth by the
[related-work](../related-work/README.md) documents and summarized as reader traits below.

Real readers are blends, so treat these as lenses to combine rather than boxes to sort into. A single
person might be an advanced Rust developer, a former Haskeller, and a hardened pragmatist at once,
and a piece aimed at them should draw on all three.

## Readers by Rust experience

How much Rust a reader commands sets the ceiling on how much CGP machinery a piece can show before it
stops teaching and starts alienating.

### The Rust newcomer

The newcomer learned Rust recently and is still absorbing ownership, borrowing, and the basics of
traits, so most of CGP's machinery sits well over their horizon. They are comfortable with structs,
enums, and method calls, have met `Clone` and `Debug`, and may still be fighting the borrow checker;
generics-heavy or type-level code is not yet vocabulary. What excites them is the promise that they
need not master a paradigm to benefit — that CGP code can *read* like ordinary functions, that an
[`#[implicit]`](../cgp/reference/attributes/implicit.md) argument looks like a normal parameter, and
that adoption is incremental.

The risk is that the full paradigm buries them: the consumer/provider split, wiring tables, and any
mention of coherence overwhelm someone still forming a model of traits, and CGP's long generated-type
errors are demoralizing to a reader who cannot parse them. Write for them by leading with the
gentlest on-ramp — a capability defined as a function, a context that gains it with no wiring at
all — keeping [`IsProviderFor`](../cgp/reference/traits/is_provider_for.md),
[`DelegateComponent`](../cgp/reference/traits/delegate_component.md), and the generated blanket impls
entirely out of sight, and reaching for familiar analogies such as a wiring table as a settings map.
Never open on coherence, and say explicitly that the whole system need not be understood at once.

### The working Rust developer

The working developer is fluent in traits and generics, ships production Rust, and judges any new
tool by whether it earns the complexity it adds. This is the pragmatic majority and the reader most
writing should target. What excites them is a concrete, familiar pain removed: two implementations of
one interface without paying for `dyn`, escaping the orphan-rule newtype dance, decoupling modules
without a dependency-injection framework — shown on code that looks like code they already write.

Their skepticism is the decisive obstacle, because they have watched "enterprise" abstraction ruin
codebases and will pattern-match CGP to that at the first sign of ceremony. Their questions are
whether it is over-engineered, what it does to compile times, how one debugs generated code, how long
a teammate takes to learn it, whether it is a lock-in risk, and — once they are actually trying it —
what it buys them while their codebase still contains a single application context, which
[message.md](message.md#the-objections-readers-bring) answers at length. Win them by leading with a problem
rather than the paradigm, showing a before/after on realistic code, and being candid about when *not*
to reach for CGP. Hold higher-order providers back for this reader in particular: composing providers
asks them to absorb functional composition on top of CGP, and two unfamiliar paradigms arriving together
is enough to lose someone who would have followed either alone. On debugging specifically, point them at
[`cargo-cgp`](../cgp/reference/cargo-cgp.md), which reshapes CGP's compiler errors to lead with the
root cause — conceding in the same breath that it is a v0.1.0-alpha handling the core wiring errors
rather than every class. Restraint earns this reader; a single overclaim loses them, often
permanently and loudly.

### The advanced Rust developer

The advanced developer commands generics, associated types, higher-ranked trait bounds, `PhantomData`,
and the coherence and orphan rules, and reads CGP fluently as trait machinery — often with delight,
sometimes with a critic's eye. Nothing about a blanket impl or a type-level table is foreign, and
they can follow an expansion without hand-holding. The enthusiast among them is excited by the
expressive power: many overlapping impls legal at once, provider selection per context, structure
encoded as type-level lists, all zero-cost and on stable Rust. This reader can become CGP's strongest
advocate, and they want the real mechanism rather than a simplified picture.

The critic among them is skeptical for informed reasons that deserve engagement rather than
deflection: the opacity of macro-generated code, the compile-time cost, the error messages, whether
the abstraction pays for itself over plain trait bounds, and the principled worry that coherence
exists for a reason. Write for them by showing the machinery honestly — the desugaring, the
`DelegateComponent`/`IsProviderFor` mechanism, and the
[coherence trade-off](../cgp/concepts/coherence.md) argued on its merits — and by treating the
[comparison to type classes](../related-work/type-classes.md) as a real intellectual exchange. Do not
dumb it down, but do not mistake fluency for approval: they still ask whether the complexity buys
genuine modularity or mere novelty, and because they shape opinion, honesty and depth matter more
here than anywhere else.

## Readers by prior mental model

Many readers arrive fluent in a paradigm CGP resembles, and the fastest way to reach them is through
vocabulary they already own. Each profile names the disposition that background brings and points to
the [related-work](../related-work/README.md) document carrying the full, cited comparison.

**The functional-programming and type-system practitioner** comes from Haskell, Scala, OCaml,
PureScript, F#, or Lean, and holds type classes, implicit parameters, row types, effect handlers, and
ML modules as native concepts. They are the audience most predisposed to become advocates, because
CGP hands them what their own languages forbid or make fragile — overlapping and orphan instances
made safe, per-context selection, extensible records and variants in a systems language. Map the
vocabulary directly (a component is a class or signature, a provider is a first-class instance, wiring
is instance resolution made explicit, an impl-side dependency is a class constraint) and lead with the
pains coherence causes them. The caution is that they are precise about their own terms and will
notice a loose analogy immediately, and some will ask why not simply stay in the functional language
whose ergonomics they prefer — answer that honestly, since CGP's value is bringing the idea to Rust's
performance and ecosystem, not out-competing the source language on elegance. Full treatments live in
[type classes](../related-work/type-classes.md),
[implicit parameters](../related-work/implicit-parameters.md),
[row polymorphism](../related-work/row-polymorphism.md),
[algebraic effects](../related-work/algebraic-effects.md), and
[ML modules](../related-work/ml-modules.md).

**The enterprise and dependency-injection developer** comes from Java, Kotlin, or C# and the Spring,
Guice, or Dagger world, and thinks in interfaces, inversion of control, testability, and object
graphs. What excites them is compile-time-checked, reflection-free injection with per-context choice —
"Dagger taken further" — where dependencies are explicit, nothing unused reaches the binary, and a
missing binding is a compile error rather than a startup exception. The vocabulary maps cleanly: a
provider is a binding, [`delegate_components!`](../cgp/reference/macros/delegate_components.md) is the
container configuration, an impl-side dependency is a constructor parameter, and
[`check_components!`](../cgp/reference/macros/check_components.md) is the graph validation a container
runs — the difference being *when* it runs. Defuse the runtime container immediately: this reader will
imagine an object holding the graph and resolving it by reflection, so say plainly that CGP's
container is the type system. The full treatment is in
[dependency injection](../related-work/dependency-injection.md).

**The dynamic-language developer** comes from Python, Ruby, or JavaScript and values duck typing and
rapid iteration. What excites them is that provider code reads like duck-typed code — sending messages
to a context it never names — while being checked so it cannot blow up at runtime. The framing that
resonates is that CGP is the mechanisms they already use with the runtime taken out. Their skepticism
is aimed at Rust as much as at CGP: they fear rigidity and verbosity, and can experience CGP's long
errors as exactly the rigidity they came to a dynamic language to escape. Be honest that runtime
malleability — plugins loaded at startup, heterogeneous collections, monkey-patching — is not what CGP
is for, and frame its late binding as late to the *wiring site* rather than to runtime. See
[dynamic dispatch](../related-work/dynamic-dispatch.md).

**The framework, library, and tooling author** builds serialization, ORMs, configuration systems, or
test frameworks, and thinks about generic-over-structure code, compile times, binary size, and derive
macros. What excites them is reaching reflection's payoff — write the framework once, have it work
over any user type — with none of reflection's runtime cost or stringly-typed failure, because CGP
encodes a type's shape as type-level lists the trait system resolves against. Their objections are
compile-time cost, error quality, that it works only on types that opted in by deriving, and that it
is not runtime introspection. Meet them by not calling CGP "a reflection system" — a reader sold on
that will look for an API to query and find trait bounds instead — and by framing it as compile-time
structural reflection encoded as types, with the opt-in requirement stated up front. This is also a
live, high-attention area, so see [reflection](../related-work/reflection.md) and
[evidence.md](evidence.md) for how to position CGP as complementary to the reflection facility the
language itself is building.

This reader profile is also the one the author's own positioning thesis targets most directly: CGP's
role is to enable people producing reusable components so that their consumers get modularity without
having to value it (see [author-personality.md](author-personality.md)).

## Readers by role and point of contact

Three further profiles matter disproportionately: two govern first impressions and adoption, and the
third governs whether CGP's ideas are taken seriously by the people shaping the language itself.

**The first-contact skimmer** is scrolling a feed, a link aggregator, or a chat channel, gives the
piece a few seconds, and will form a snap judgment they may broadcast. What earns them is a sharp,
concrete hook — a one-line value proposition or a striking before/after — that sounds novel and real
at once. What loses them is anything that lets them pattern-match CGP to a category they already
dismiss: "just another DI framework", "macro magic", "over-abstracted Rust", "just use traits". One
phrase that reads as pretentious and they bounce, or worse, dunk. Write for them by leading with the
single clearest benefit on concrete code, preempting the obvious dismissals in the opening lines, and
keeping jargon out of the first impression. Because they shape CGP's reputation out of all proportion
to the time they spend, the whole strategy lives or dies in the first few lines they see.

**The evaluator and decision-maker** is a tech lead, staff engineer, or architect weighing adoption
for a team, and reads for risk as much as benefit. What moves them is maintainability, testability,
decoupling, performance guarantees, and reduced boilerplate at scale, backed by evidence that it works
in real systems. Their skepticism is about cost they will own: ramp-up and hiring, the maturity of a
young paradigm, how the code is debugged, and the wisdom of betting a codebase on something novel.
Reach them with candour rather than enthusiasm: be honest about maturity, show that CGP is a superset
of ordinary traits so it can be adopted incrementally and stepped back from, and state plainly where
it fits and where it does not. Address "can my team learn this" head-on rather than letting it fester.
Overselling is fatal here, because this reader's job is to discount hype.

### The language-design and compiler-team reader

The language-design reader works on Rust itself or writes about where it should go: compiler-team
members, the people publishing design posts on traits and coherence, and the readers who follow them.
They hold the coherence rules, the trait solver, and the desugarings not as advanced knowledge but as
their subject matter, so nothing in CGP needs simplifying for them and any imprecision is immediately
visible. What interests them is not whether CGP is useful but whether it is *evidence*: a paradigm that
implements, on stable Rust and in production code, a fragment of something the language is considering
building is a data point about feasibility, ergonomics, and what the desugaring actually costs.

This reader is unreachable through the general channels and is reached only by engaging a live design
question at their level. Two rules govern a piece written for them, and both invert the usual advice.
**Precision beats accessibility** — the audience-tuned one-liners and the vocabulary schedule are for
somebody else, and hedged prose reads here as not having thought it through. And **the concessions are
the contribution**: what CGP does *not* solve — the formalization goal, migrating the existing trait
ecosystem, the parts of a full dictionary-passing design it cannot express — is more useful to a
language designer than the parts it does, because that is the boundary they are trying to map. A piece
that positions CGP as a competitor to a language feature loses this reader in a paragraph; one that
positions it as an existence proof with a stated edge is the rarest kind of contribution the project
can make.

The opportunity is also perishable in a way no other profile's is. It exists only while a matching
conversation is live, so a piece for this reader is worth writing when the conversation is happening
rather than when the project's own schedule is clear. The current attachment points are in
[evidence.md](evidence.md#the-conversations-that-draw-attention).

## What nearly every reader shares

A few things hold across every profile, and they are the highest-leverage moves any piece can make.
The universal question underneath all of them is *is this worth the complexity?*, and the only
convincing answer is a concrete problem solved plus honest limits. Three misunderstandings recur
across nearly every audience and should be preempted early: that CGP has runtime cost or a runtime
container, when its wiring is resolved at compile time and erased; that it is "just another DI
framework" or "just macro magic", when it is a trait-level paradigm with static guarantees; and that
using it requires understanding all of its internals, when its vanilla-looking idioms let it be
adopted a little at a time.

The default reaction to CGP is the reflex to pattern-match it to something already familiar and
dismissible, so the writer's real job is to make the genuinely novel part legible before that reflex
fires. When a piece must serve a mixed audience, default to satisfying the pragmatic skeptic and the
first-contact skimmer, because they are the least forgiving and the most numerous, and writing that
wins them rarely loses anyone else.

## The comprehension barriers

A reader can genuinely *want* to understand CGP and still fail to, because its concepts sit on a
stack of Rust knowledge not every developer has — and that is a different problem from skepticism.
Skepticism is about *willingness*: a reader who understands CGP but doubts it is worth the
complexity. A comprehension barrier is about *ability*: a reader who would happily use CGP but cannot
follow the explanation. A piece has to clear both, and confusing them is a common failure, since
answering an ability problem with a persuasion argument leaves the reader no better able to read the
next line.

The encouraging fact is that CGP's own design already lowers most of these barriers, because its
ergonomic constructs exist precisely to let a reader use a capability without first understanding the
harder concept beneath it. That turns much of the job into *using those affordances well*, and doing
so is not a simplification that misleads — the ergonomic forms are the
[recommended way to write CGP](../cgp/guides/README.md), so leading with them shows the idiom rather
than a beginner's dialect to unlearn.

The barriers form a **prerequisite ladder**. Near the bottom sit generic parameters and traits with
bounds, which a surprising share of working Rust developers are uneasy with; above them come blanket
implementations and associated types, which many have used but few reason about fluently; and near
the top sit coherence and the orphan rule, and type-level programming with higher-ranked bounds,
which only the advanced audience holds. The recurring mistake is assuming the reader stands higher on
the ladder than they do, because CGP's author and its most enthusiastic readers stand near the top.

One barrier below is different in kind from the rest and worth flagging before the list. Most of these
are things a reader finds *hard*; the application-context shape is something they have never had a reason
to *imagine*, because vanilla Rust makes it legal and pointless at the same time. A barrier of missing
concepts is not lowered by simpler wording — it is lowered by building the concept out of code the reader
can check.

### Generic parameters are intimidating

The largest barrier by far is that many Rust developers disengage the moment they see a signature
bristling with `<T>` and bounds. Written naively, CGP is generic-heavy — provider traits carry an
explicit context parameter, methods thread `Code` and `Input` parameters — so a reader who bounces on
generics bounces on CGP before any value lands.

CGP answers this with constructs that let a reader write real CGP with no generic parameter in sight.
[`#[cgp_fn]`](../cgp/reference/macros/cgp_fn.md) turns a capability into a plain function whose
simplest form shows no generics at all; [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md) lets a
provider omit the context parameter and the `for Context` clause; and
[`#[implicit]`](../cgp/reference/attributes/implicit.md) makes context values look like ordinary
arguments. Lead every introduction with these, introduce a generic only at the first moment it earns
its place, and never open with a raw provider-trait signature. **Show that CGP code can look like the
Rust the reader already writes, rather than reassuring them the generics are not as scary as they
look** — the demonstration persuades where the reassurance does not.

Rust's own designers used exactly this move, and pointing at it is a useful precedent when the strategy
needs defending. `&impl Trait` and `&dyn Trait` read almost identically at the call site while the first
is generics and the second is dynamic dispatch, so a developer moving from one to the other adopts
monomorphized generics without registering that they have — the syntax did the teaching that an
explanation would not have. `#[cgp_fn]` and `#[implicit]` do the same job for CGP, which is why they are
the entry point rather than a simplification of one.

### The provider trait reads inside-out

A distinct and disorienting barrier is that a raw provider trait turns Rust's conventions inside-out:
the original `Self` moves to a zero-sized provider marker and the context becomes an explicit type
parameter, so `self` and `Self` no longer mean what instinct says. A reader meeting this cold must
hold an inversion in their head before reading a single provider body, and it is one of the most
common places understanding stalls.

[`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md) exists to remove it: it keeps `self` and `Self`
meaning the context, lets the author omit `for Context`, and puts the provider name in the attribute,
so a provider reads like an ordinary trait impl. Present it as *the* way to write a provider and keep
the inside-out [`#[cgp_provider]`](../cgp/reference/macros/cgp_provider.md) shape out of introductory
material; when the raw form must be shown, say plainly and up front that here `self` and `Self` are
the context. Introducing the
[consumer/provider split](../cgp/concepts/consumer-and-provider-traits.md) by leading with the raw
provider trait is the surest way to lose a reader who would have followed `#[cgp_impl]` fine.

### A type can stand for your whole application

A barrier that looks like vocabulary and is really a missing concept: readers do not know what an
"application context" *is*, because vanilla Rust gives them no reason to have built the idea. The shape
is legal — `impl CanEncodeValue<Vec<u8>> for ApiServer` compiles, and alongside the same impl for
`Firmware` it genuinely gives per-application encoding with no CGP at all — but every context-and-type
pair needs its own hand-written body and nothing can be factored out, because a blanket impl would
overlap. So the arrangement is **available and unrewarding**, it dies at three types, and nobody carries
it in their repertoire. A reader is then handed the phrase "application context" and has no shape to
attach it to.

This is why naming the thing does not work. **The concept has to be built, and it can be built out of
plain Rust the reader can verify**, in three steps. First show the vanilla version working — two
application types, one value type, two different encodings — so the unfamiliar arrangement turns out to
be ordinary Rust they simply never had a reason to write. Then show it not scaling: add a third value
type, then try to factor the shared logic into a blanket impl and hit `E0119`. Only then name it, at the
point where the reader already wants what it provides.

Two concrete anchors carry more than the definition. **Say that such a context usually has no fields** —
`struct AppA;` is a complete context, and an empty struct with traits on it is otherwise unreadable. And
**name what it replaces in the reader's own world**: a config struct, an axum `State`, a Spring
`@Configuration`, a Dagger module — the application's configuration lifted to the type level so the
compiler resolves it.

One framing follows from all this and is worth using wherever the payoff is stated: coherence does not
*forbid* the application-context shape, it makes it **not worth building**. So CGP's contribution is
constructive rather than permissive — it does not merely escape a rule, it makes an available shape worth
using. That is a harder claim to dismiss as cleverness than "we work around coherence", and it is the
same move as explaining what Rust already does before improving on it. The technical account is in the
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md), and the wording rules are in
[vocabulary.md](vocabulary.md#qualifying-a-context-and-a-target).

### The trait a reader would design hides the payoff

A barrier that produces no confusion whatsoever and still loses the reader: the trait shape most
developers reach for first is the shape CGP pays least for. Asked to model shapes, a reader with any
object-oriented training writes `Shape` carrying `area`, `perimeter`, `scale`, and `rotate` — a coherent
entity, one word for a team to use, and how most people were taught to model a domain. CGP accepts that
trait, and then very little about it is reusable: a provider must answer the whole surface, a wrapper must
forward every method it has no opinion about, and a context that only computes areas still has to supply a
`rotate` body and an `Angle` type. The reader concludes from a fair experiment on their own code that CGP
is ceremony, and *within the design they chose they are right*.

This barrier sits here rather than among the objections because it is not a doubt to be answered: the
reader is willing, and the shape of their first attempt is what made the value unavailable. Persuasion
cannot reach it. The teaching move is to show the contrast on code — a single-decision `AreaCalculator`
wraps in four lines and composes over any inner calculator, while the same wrapper over `Shape` is mostly
passthrough — and to hand the reader the checkable smell, which is that a consumer trait named after a noun
rather than a verb usually holds several decisions. The costs and the splitting procedure are in
[sizing a component](../cgp/guides/sizing-a-component.md).

**Delivering this correction badly is worse than not delivering it, and the failure is specific: the reader
concludes CGP traits are limited to one item.** Because idiomatic CGP is dominated by single-method
components, teaching material that shows only those reads as a restriction the macros impose rather than a
recommendation the author can weigh — and a developer who believes their traits are being capped gets
defensive about the whole paradigm rather than engaging with the guidance. This has been observed in
practice, and it can lose a reader before they try anything. Three rules follow, and the first is the one
that does the work. **Show a multi-item component working before recommending anything about grouping** —
CGP's own `CanCompute` and `CanHandle` declare an associated `Output` beside their method, so the
demonstration costs one snippet and is not a concession. **State the non-limitation as a fact rather than a
permission**: a component trait is an ordinary trait taking as many methods, associated types, and consts
as any other. And **frame the guidance as a cost curve the reader prices**, not a rule they comply with —
grouping items one provider choice decides together collects more reuse, and how much that is worth is
their call on their codebase.

### Bounds on the context are a barrier of their own

Below the inversion sits a plainer barrier: some readers are shaky on traits at all, and even fluent
ones find `where Self: SomeTrait` unusual, because bounding the implementing type is uncommon in
everyday Rust and reads as machinery rather than intent. Two constructs lower it.
[`#[cgp_fn]`](../cgp/reference/macros/cgp_fn.md) needs no trait at all — the reader writes a function
and never meets a trait definition — which makes it the gentlest possible entry point. And
[`#[uses]`](../cgp/reference/attributes/uses.md) turns a `Self: Trait` dependency into a line that
reads like a `use` import of a capability. Start the least experienced reader on `#[cgp_fn]` with no
mention of traits, and introduce `#[uses]` as "importing a capability the code relies on", deferring
the `where`-clause reality until the reader cares.

### Traits that are "magically" implemented

Once a reader meets a getter trait, [`#[cgp_auto_getter]`](../cgp/reference/macros/cgp_auto_getter.md)
generates a blanket impl, so the trait is satisfied without the reader writing any impl, and its
method is callable only when the trait is in scope. Both halves confuse a newcomer, and together they
make the system feel like it is doing things behind their back.
[`#[implicit]`](../cgp/reference/attributes/implicit.md) sidesteps the tangle entirely: a value is
read from a context field as an ordinary argument, with no getter trait, no blanket impl to reason
about, and nothing to import. Make implicit arguments the default way a reader learns to pull values
from a context, and introduce getter traits only for the narrow cases an implicit argument cannot
reach, and only once the reader is past the intimidation stage.

### Associated types and qualified paths

Abstract types raise a barrier through syntax as much as concept: naming a context's abstract error
means `Self::Error`, or in full `<Self as HasErrorType>::Error`, and projections of that shape
intimidate and clutter. [`#[use_type]`](../cgp/reference/attributes/use_type.md) removes it by letting
the reader import an abstract type and write the bare name, with the qualified path filled in and the
bound added — which reads like a `use` for a type, a model the reader already owns. Present it exactly
that way, and keep hand-written `Self::`-qualified syntax out of introductory material, bringing it in
only for a construct's own local associated type, where it genuinely belongs.

### The wiring table and its machinery

Wiring raises a barrier of abstraction: a type-level lookup table,
[`DelegateComponent`](../cgp/reference/traits/delegate_component.md), and component-name markers are
all machinery a reader would otherwise have to absorb before believing a context "has" a capability.
The surface is already simple — a [`delegate_components!`](../cgp/reference/macros/delegate_components.md)
table is a compact list matching each capability to the implementation supplying it — so describe it
with a plain analogy, a settings map or a lookup table, and keep `DelegateComponent` and
`IsProviderFor` out of a beginner's view, since they are the mechanism rather than the model.
Mentioning that the table is resolved at compile time and compiles away doubles as the reassurance
that the abstraction has no runtime cost.

### Reading the error messages

The one barrier design can lower but not remove is the error message: a mis-wired context can produce
a wall of generated types, and understanding that wall requires exactly the machinery a beginner is
avoiding. This is where a reader who was following comfortably gets thrown, because the failure
speaks in a register the ergonomic surface had spared them.

The mitigations are real and one of them is now a dedicated tool. The oldest is
[`check_components!`](../cgp/reference/macros/check_components.md), which forces the failure to
surface at the wiring site and names the actual missing dependency rather than letting it erupt far
away; the [errors catalog](../cgp/errors/README.md) documents the recurring shapes. The newest is
[`cargo-cgp`](../cgp/reference/cargo-cgp.md): run with `cargo cgp check` in place of `cargo check`, it
turns on Rust's next-generation trait solver to **un-hide** the dependency errors the default solver
suppresses — recovering the root cause of the worst class, where plain `cargo check` reports only that
a method's bounds are unsatisfied and never names the missing field — and then rewrites the classes it
recognizes to lead with that cause, tagging each with a `[CGP-Exxx]` code.

Hand the reader the tool early and teach them to read the root cause first, while setting the
expectation with full honesty: CGP's raw diagnostics can be verbose, a check localizes them, and
`cargo cgp check` reshapes the recognized classes — but the tool is a v0.1.0-alpha that does not yet
reshape every class, leaving some (orphan-rule errors among them) passing through as the compiler
wrote them. **The honest frame is that the error experience is dramatically better and actively
improving, not solved.** This is the one barrier where pretending it away costs more trust than
admitting it.

A second mitigation now exists and is worth naming *here*, beside the cost, rather than anywhere more
prominent. Decoding a generated-type cascade is mechanical work over a vocabulary that is written down,
which is the kind of work a coding agent does well — and CGP publishes a
[skill](https://github.com/contextgeneric/cgp-skills) that teaches an agent that vocabulary. A reader
who already works with an assistant can attach it and check the claim within the hour, which is what
makes it sayable at all. Two constraints keep it honest. **Say it as a mitigation, not as an answer**:
the diagnostics are still verbose, and a reader who wants to work without an assistant must not be told
their problem is solved. And **never lead with it** — a project that opens on AI in 2026 is heard as
chasing attention, and this is the audience least willing to extend the benefit of the doubt. The same
rule holds for the learning curve and the wiring volume, which the skill reduces for the same reason
and which should be conceded the same way.

### Knowing where to start, and why it is worth it

Two meta-barriers sit above the individual constructs. The first is breadth: CGP has many pieces, and
a reader who cannot see the minimal path assumes they must learn all of it before writing anything.
The [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) is the answer to hand them — start
at the lowest tier that solves the problem — and a piece should give an explicit on-ramp rather than a
tour of the whole surface. The second is motivation: a reader who can parse the syntax may still not
grasp *why* the consumer/provider split earns its keep, so the mechanics read as ceremony. Lead with a
concrete problem the reader has felt and defer the coherence theory that explains the split at a
deeper level.

### The teaching discipline this points to

The barriers share one strategy, and it can be run as a checklist before publishing anything
instructional. **Say which shape an example is in**, since a piece that shows a value context and then an
environmental one without marking the change leaves the reader unable to say what a context is — the
qualifiers and the four misreadings they prevent are in
[vocabulary.md](vocabulary.md#qualifying-a-context-and-a-target). **Disclose progressively**, leading
with `#[cgp_fn]`, `#[cgp_impl]`, `#[implicit]`, `#[uses]`, and `#[use_type]`, and revealing the machinery
beneath only when a reader needs it.
**Teach the ergonomic idioms as the idiom**, since they are the recommended forms rather than a
simplified dialect. **Show the granularity, not only the constructs**, because a reader who groups every
operation of an entity into one component collects none of the reuse and reasonably blames CGP for it.
**Motivate before mechanism**, opening on a concrete problem rather than the
consumer/provider split. **Introduce vocabulary gradually and by analogy**, deferring "generic",
"blanket impl", "coherence", and "monomorphization" until needed. **Show rather than reassure**,
because demonstrating that CGP code looks like plain Rust convinces where "it's not that hard" does
not. And **be honest about the barrier design cannot remove**, pointing at `check_components!` and
`cargo cgp check` while conceding the tool's youth.

One caveat specific to CGP cuts against a strict reading of progressive disclosure, and it is
deliberate: Rust programmers do not trust generated code they have not seen through, so **showing the
desugaring is itself a teaching move rather than a distraction**. The
[tutorial writing guide](../website/writing-guides/tutorial.md) makes this concrete.
