# Writing an explanation page

An explanation page exists to make a reader **understand** something about CGP that they were not going
to reach by following a tutorial or looking up a construct. Its reader is not doing anything while they
read — no editor open, no compiler running — so the page's whole job is to leave them holding an idea
they did not have before, and able to repeat it.

This is a **new page type** on the site. The docs tree previously held orientation (the Introduction),
a feature-and-benefit summary (the Overview), a link directory, a contribution page, the tutorials, and
an inlined copy of the agent skill — none of which explain CGP's ideas at length to a public reader. The
tier exists for two reasons at once. The [homepage guide](homepage.md) offloads to it, so everything
that outgrows a homepage section becomes one of these pages; and the site needs a public counterpart to
the internal [cgp/concepts/](../../cgp/concepts/README.md) catalog, so that every cross-cutting CGP idea
has somewhere a reader can be sent.

The second reason decides the tier's shape: it is the **Concepts** section, with **one page per idea**,
mirroring the internal catalog one to one — eighteen pages plus a hand-written index. The four pages the
homepage offloads to are four of those eighteen rather than the whole tier; which concept page plays
each role is recorded in [information-architecture.md](../information-architecture.md), and the current
state of the section in [site-structure.md](../site-structure.md).

- **Where they live** — `docs/concepts/`; see
  [Placing them in the docs tree](#placing-them-in-the-docs-tree)
- **Voice** — project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), with one real tension
  worked out below
- **Raw material** — [cgp/concepts/](../../cgp/concepts/README.md), rewritten rather than copied

## What an explanation page is not

Three page types sit next to this one and the boundaries are worth stating, because a draft that drifts
across one stops serving anybody.

A **tutorial** teaches a reader to do something, and is judged on whether they got there. It carries the
reader step by step and withholds anything they do not need yet, per [tutorial.md](tutorial.md). An
explanation page assumes nobody is following along, which is exactly what frees it to take the long way
round, discuss alternatives, and admit complications a tutorial must suppress.

A **reference page** specifies a construct completely and is read in fragments by someone looking one
thing up. Its published home is the site's own reference tier, which is
[canonical rather than a supplement to rustdoc](reference.md) and is ported from the exhaustive internal
[cgp/reference/](../../cgp/reference/README.md). An explanation page names constructs but never
enumerates their syntax — the moment it starts listing accepted forms, it has become a bad reference.

The **homepage** makes the idea click in one screen and one bounded essay. An explanation page is where
that essay's material goes when it needs room. The relationship is one-directional and worth keeping
that way: the homepage links down, and the explanation page does not try to re-earn the reader's
attention, because they have already given it.

## What every explanation page owes its reader

Six obligations hold across the tier.

**Answer "why", not "how do I".** The organizing question of the page is a question a reader would
actually ask out loud — *why can't Rust do this?*, *what is actually generated?*, *should I use this?* —
and the page is finished when that question is answered. If the natural next sentence is "now add this to
your `Cargo.toml`", the material belongs in a tutorial.

**Explain the existing thing properly before improving on it.** This is the project's frame and its
author's most consistent habit: CGP
[enhances Rust's trait system rather than replacing it](../../communication-strategy/identity.md), so a
page that opens by describing coherence as a limitation has the argument backwards. The
[RustLab transcript](../blog/rustlab-2025-coherence.md) is the model — roughly ten slides establishing
that the trait system's global lookup gives Rust free transitive dependency injection, and that
coherence is therefore *correct*, before a word about working around it.

**Be as long as the idea needs, and say so at the top.** Length is not a failing here; ambushing the
reader with it is. Open with a sentence or two saying what the page covers and roughly how far it goes,
the way the [Hypershell post](../blog/hypershell-release.md) opens with a reading estimate and a
section-by-section preview. A reader who knows the shape navigates; a reader who does not, abandons.

**Show code as illustration, not as steps.** Snippets on an explanation page exist to make an argument
concrete — this is the impl Rust rejects, this is what the macro generates — and are read rather than
typed. They may elide bodies with `/* ... */`, they need not build to a runnable program, and they
should never be numbered or sequenced as instructions.

**State the cost.** Every page in this tier names what its subject costs or where it stops applying,
because these are the pages a skeptic reads all the way through and the ones an evaluator quotes.

**End by routing, not by concluding.** A summary paragraph that restates what the reader just read is
wasted space. Send them to the tutorial that puts the idea to work, the neighbouring explanation page, or
the reference that specifies it.

## What Diátaxis gives this tier, and where CGP diverges

Diátaxis's account of explanation is the most directly usable part of the framework for this site, and
most of it is adopted without qualification. Explanation is **understanding-oriented** and read away from
the work. It may **discuss alternatives and history**, which a tutorial must not. It should **make
connections** between ideas rather than treating each in isolation. And it explicitly permits **opinion
and judgement**, which reference and tutorial do not.

Two divergences matter, and both are consequences of decisions made elsewhere.

**Opinion is allowed but must not be personal.** Diátaxis is right that explanation is where a project
says what it thinks, but the website speaks in the **project voice** — the first-person, personally
candid register belongs to the blog. Resolve this by grounding the judgement rather than attributing it:
"this is more machinery than a plain trait needs" rather than "I think this is more machinery than a
plain trait needs". Where an argument genuinely depends on the author having made a choice and having
reasons, the page states the reasoning impersonally and links to the blog post or the transcript where
he makes it in his own voice.

**The reference boundary is softer here than Diátaxis draws it.** Diátaxis keeps mechanism out of
explanation, but CGP's central credibility problem is that its macros generate code, and a Rust
programmer will not adopt what they cannot see through — the same reason
[a tutorial must show the desugaring](tutorial.md). So *How CGP works* is deliberately a page about
mechanism, and any explanation page may show generated code where showing it is the argument. The line
that still holds is enumeration: showing what a macro produces is explanation, listing every form it
accepts is reference.

## Turning a concept document into an explanation page

The raw material for this tier is [cgp/concepts/](../../cgp/concepts/README.md), which already contains
careful, verified accounts of every idea these pages need. **They are not copy-paste sources.** A concept
document is written for an agent that has loaded the `/cgp` skill, so it uses "provider trait",
"impl-side dependency", and `IsProviderFor` as known vocabulary and links sideways into the reference for
anything it does not carry. A public reader has none of that.

Three transformations turn one into the other. **Apply the vocabulary schedule**: defer or gloss the
terms [vocabulary.md](../../communication-strategy/vocabulary.md) says to defer, and introduce the rest
with a plain-language definition on first use. **Add the motivation the concept document assumes**: a
concept opens with what the idea *is*, whereas an explanation page opens with the problem that makes the
idea worth having. And **remove the internal machinery** — `DelegateComponent`, `IsProviderFor`, the
`Symbol<…>` spine — unless the page's subject *is* that machinery, in which case introduce it as the
mechanism behind the model rather than as the model.

The synchronization rule applies unchanged in both directions: an explanation page's claims are bound to
the source exactly as a concept document's are, and a change to the underlying behavior updates both.

## The page shape

Every page in the tier follows the same shape, which is looser than a reference page's fixed template
because an explanation is an argument rather than a specification, and firmer than nothing because a
reader who has read one page should be able to skim the next by habit.

**Open by naming the question and saying where the page ends.** A sentence or two: what the page
answers, and what it closes on. This is the declared-length habit at the scale of a single page — a
reader who knows the shape navigates, and one who does not, abandons.

**Develop the idea in as many sections as it takes**, with the argument's own headings rather than
prescribed ones, and with code shown as illustration rather than as steps.

**Close with two fixed sections, in this order.** *What it costs* names what the idea costs or where it
stops applying, and is not optional — these are the pages a skeptic reads to the end. *Where to go next*
routes to the neighbouring concept, the tutorial that puts the idea to work, and the reference pages
that specify the constructs, rather than summarizing what the reader just read.

The written [Consumer and provider traits](https://contextgeneric.dev/docs/concepts/consumer-and-provider-traits)
page is the model, and it shows what the shape looks like when the argument is about a mechanism.

## The four pages the homepage offloads to

The homepage's [offload rule](homepage.md) names four destinations, and each is now a page of the
Concepts section rather than a separate artifact: *Why CGP exists* is **Bypassing coherence**, *How CGP
works* is **Consumer and provider traits** with **Impl-side dependencies** beside it, and *When to use
CGP* is **How much CGP to use**. The fourth, *Project status*, is project meta rather than a CGP idea
and does not belong among the concepts; its home is unsettled, per
[information-architecture.md](../information-architecture.md). The specifications below still stand for
the pages they describe — read each one as the spec for the concept page that plays its role.

### Why CGP exists

**The most valuable page missing from the site**, and the one the homepage links to most. Its organizing
question is *why can't Rust do this already?*, and it is the long-form version of the homepage's first
two essay sections.

The argument runs in five movements. Establish that **Rust's trait system doubles as a
dependency-injection mechanism** — a generic impl can require `where T: Display` without any caller
naming it, and the compiler resolves that bound and every transitive bound beneath it. Show that this
**only works if every lookup finds the same implementation**, which is what the overlap rule and the
orphan rule buy, so coherence is a guarantee rather than a restriction. Then show **what the guarantee
costs**, concretely: two blanket impls that could both match one type are rejected even when the author
knows which should apply, and a trait cannot be implemented for a type from another crate. Then the
**workarounds** — the newtype dance, and the marker-struct-plus-helper-trait pattern developers
[independently reinvent](../../communication-strategy/evidence.md) — because the reader has written one
of these and recognizing it is what makes the next movement land. Finally the **move**: the
implementation's `Self` becomes a type the implementing crate owns, so neither rule bites; and coherence
is **restored locally**, because each context names exactly one provider, so no call site is ambiguous.
"Coherence is not repealed — it is scoped" is the sentence the page exists to earn.

Built from [coherence](../../cgp/concepts/coherence.md) and
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), with the
[RustLab transcript](../blog/rustlab-2025-coherence.md) as the model for pacing and the
[modular serialization example](../../examples/modular-serialization.md) for verified code. It should
name the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) at the end, because a reader
who has just been told coherence can be escaped needs to hear immediately that most code should not.

#### The sixth movement: the shape the page has to build

The five movements above leave the reader believing overlapping implementations can be made safe, and
then the page has to do one more thing that no other surface on the site can: **build the idea of a type
that stands for the application.** This is a missing concept rather than a hard one — vanilla Rust makes
the arrangement legal and pointless at once, so a reader has never had a reason to construct it, and
handing them the phrase "application context" therefore lands as an unfamiliar noun. The full account is
the [comprehension barrier](../../communication-strategy/readers.md) of the same name; on this page it
runs in three steps.

**Show the vanilla version working.** Two application types, one value type, two encodings, no CGP:
`impl CanEncodeValue<Vec<u8>> for ApiServer` beside the same impl for `Firmware`. This compiles, and
showing it is what converts an unfamiliar shape into ordinary Rust the reader simply never had a reason to
write. **Show it not scaling**: a third value type, then an attempt to factor the shared logic into a
blanket impl, then `E0119`. **Then name it**, at the point where the reader already wants what it
provides — and say in the same breath that such a context usually has no fields, because `struct AppA;`
is otherwise unreadable.

The payoff is then available in its strongest form, and the page should state it: coherence does not
forbid this shape, it makes it **not worth building**, so CGP's contribution is constructive rather than
permissive. It does not merely escape a rule; it makes an available shape worth using.

#### Two transitions this page must not leave silent

The site's examples move through three shapes — a value context whose target is `Self`, an environmental
context whose target is `Self`, and an environmental context targeting a parameter — and **both
transitions between them are currently unmarked everywhere**. Each needs one sentence, and this page is
where they belong, because it is the page that has the room.

The first is the harder one, precisely because nothing signals it: going from `String: CanEncode` to a web
application's `App: CanQueryUser` changes no signature and adds no parameter, yet `Self` has stopped being
data. Mark it — *"until now the wired type has been the data; from here it is a type you define to stand
for your application, and that change alone is what escapes coherence, because you can define as many as
you like"* — and note that this, not the parameter, is where the restriction lifts. The second is the
visible one: *"the context can already decide for itself; to let it decide for a type you don't own, the
value moves out of `Self` and becomes a parameter."*

Use the qualifiers from
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target) — value
context, environmental context, self-targeted, parameter-targeted — and introduce each at the transition
it explains rather than as a glossary up front.

### How CGP works

The page for the reader who believes the pitch and now wants to see through the macros. Its organizing
question is *what is actually generated, and what does it cost?*, and it is the site's direct answer to
["macros are magic"](../../communication-strategy/message.md#the-objections-readers-bring).

It covers, in order: the **two traits** one definition produces and why the split is what makes the
overlap legal; the **wiring table** as a compile-time lookup, described with the settings-map analogy
before any trait name; **what a call actually resolves to**, traced once end to end; the **plain Rust** a
small example expands into, ideally straight from
[`cargo cgp expand`](../../cgp/reference/cargo-cgp.md) so the reader can reproduce it; and **why none of
it costs anything at runtime** — no vtable, no container, nothing in the binary for an unused provider.
It should also explain, briefly, that **wiring is lazy** and that this is why a check exists, which is
the honest setup for the errors discussion.

Built from [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md),
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md), and
[check traits](../../cgp/concepts/check-traits.md). This is the one page in the tier where
`DelegateComponent` and `IsProviderFor` may be named, because the page's subject is the mechanism — but
they arrive late, after the model has landed, and are introduced as the machinery behind it.

### When to use CGP, and when not

**Not an explanation page** — it is a decision guide, and it follows the rules of one: it exists to be
acted on, so it is shorter, more scannable, and may use a table where an explanation page would use
prose. It sits in this tier because the homepage's cost section needs somewhere to hand a skeptic, and
because nothing on the site currently draws CGP's boundary in public.

Its content is [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp) rendered
for a public reader: the rule of thumb, the alternative-by-alternative guide with each alternative's home
ground conceded first, and the cases where CGP is simply the wrong tool. Two rules bind it especially
tightly. **Never disparage the alternative** — represent each as its own users would recognize it. And
**if a table is used, every row must concede a case where the other tool wins**; a table showing CGP
winning everything reads as a strawman and loses the reader it was written for. The technical map behind
it is the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md).

Because the page's whole subject is where CGP's costs outweigh its benefits, it is also one of the two
places the **agent-support mitigation** belongs: the learning curve, the diagnostics, and the wiring
volume are three of the costs a reader is weighing here, and CGP's published agent skill genuinely
changes their size. State it where those costs are discussed, as a smaller cost rather than a
disappearing one, and do not let it soften a boundary — a codebase that will only ever have one
application still belongs on `#[cgp_fn]` alone, regardless of who writes the wiring.

This page also carries a second decision the others do not: **which of CGP's three shapes to reach for.**
Some readers will resist being taught three where they expected one, and the defence is to show that each
answers a different question rather than representing a different amount of sophistication. Two questions
settle it, and they should appear as questions rather than as a taxonomy: *is the capability about the
data, or about the application?* — about the data means a value context and the retrofit shape, about the
application means an environmental context. And *does it concern a type you don't own, which different
applications must treat differently?* — if so the target moves into a parameter, and if not, self-targeting
is enough.

Presented that way the shapes read as a decision the reader is already equipped to make. Presented as
three named forms to learn first, they read as the complexity the page exists to disarm. State plainly
that the application shape is where most CGP code lives, so the reader knows the common case rather than
inferring that the most elaborate shape is the intended destination.

### Project status and adoption risk

**Also not an explanation page** — it is project meta, and it is the page an evaluator arrives looking
for. Most of it already exists as the "Current Status" section of the
[Introduction](../site-structure.md) and should be lifted into a page of its own so the homepage can link
it directly from above the fold.

**Its frankness is the asset and must survive the move.** It currently tells readers that CGP is in
formative early stages, that the rough edges are real, and that adopting it for mission-critical work
carries risk — and that candour is doing more persuasive work for the evaluator profile than any claim on
the site. Do not soften it into marketing. Four things should change: the stale year-stamp; the absence
of any mention of [`cargo-cgp`](../../cgp/reference/cargo-cgp.md), which directly answers two of the
rough edges the page lists; the missing incremental-adoption reassurance, that CGP is a superset of
ordinary traits and can be adopted in one corner and stepped back from; and a sentence on CGP's
published agent skill among the mitigations, since the learning curve and the diagnostics this page is
honest about are two of the three costs it reduces. That last one belongs here precisely because this is
a page about risk — stated beside a cost it makes smaller, never as a capability, per
[message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these).

## Placing them in the docs tree

The sidebar is autogenerated from the `docs/` directory tree, so these pages need a directory with a
`_category_.json` and `sidebar_position` front matter; see [site-structure.md](../site-structure.md) for
the mechanics and for the stock-Docusaurus policy that constrains anything more elaborate.

**Do not name the category after the framework.** "Explanation" is a term for the people organizing the
documentation, not for the people reading it, and Diátaxis itself advises against exposing its own
vocabulary in navigation. The category is labelled **Concepts**, which names the same thing plainly and
matches the word the knowledge base already uses for these documents, so the internal and public names
agree.

The section sits at `docs/concepts/`, between Tutorials and Reference, and its pages are ordered in the
sidebar as a reader meets the ideas rather than as the internal catalog lists them: the coherence
problem and the trait split first, then the three faces of dependency injection, then composition and
scale, then the applied ideas, with the `Send`-bound workaround and the how-far-to-go decision guide
last. The order and its reasoning are recorded in
[information-architecture.md](../information-architecture.md#navigation-and-sidebar-order).

Two consequences for neighbouring pages follow and should land in the same change. The
[Introduction](../site-structure.md) currently carries both the maturity discussion and the routing
advice; once *Project status* exists, the Introduction keeps the routing and links to it. And the
Introduction's "Getting Started" section currently sends readers to blog posts as the most current
material, which was true before the tutorials existed and is now the weaker answer.

## What must not be on an explanation page

**No instructions.** No install steps, no "add this to your `Cargo.toml`", no numbered sequence to
follow. The moment the reader is expected to be typing, the page has become a tutorial with the teaching
removed.

**No exhaustive syntax.** Naming a construct and showing one use is explanation; listing its accepted
forms is reference, and it belongs on the [reference page](reference.md) for that construct.

**No first-person narration.** Project voice throughout. Where the argument wants a person behind it,
link to the [transcript](../blog/rustlab-2025-coherence.md) or the blog post that has one.

**No unmotivated mechanism.** Every piece of machinery a page shows must answer a question the page has
already made the reader ask. `IsProviderFor` on *How CGP works* is earned; `IsProviderFor` on *Why CGP
exists* is not.

**No claim without its cost.** These are the pages read end to end by the least credulous readers, so an
unqualified capability claim does more damage here than anywhere else on the site.

## Checking a draft

**State the page's organizing question and check the page answers it** — and only it. A page answering
two questions is two pages, and the second one is the essay that should have been offloaded.

**Check the frame.** Does the page explain what Rust already does, correctly and sympathetically, before
improving on it? This is the single most common way a CGP explanation goes wrong.

**Find the cost.** If the page makes a claim and never names its limit, it is not finished.

**Check the voice.** Project voice, no first person, and any judgement grounded rather than attributed.

**Check what leaked in.** No install steps, no syntax tables, and no internal machinery the page has not
earned.

**Verify every snippet** against the source and the `/cgp` skill, preferring code already verified in
[examples/](../../examples/README.md), and remember that a concept document is a rewrite source rather
than a copy source.
