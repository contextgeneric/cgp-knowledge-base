# Writing an explanation page

An explanation page makes a reader **understand** something about CGP that following a tutorial or
looking up a construct would not give them. Its reader has no editor open, so the page's whole job is
to leave them holding an idea they did not have, and able to repeat it.

This is the site's **Concepts** tier: one page per idea, mirroring the internal
[cgp/concepts/](../../cgp/concepts/README.md) catalog one to one, so every cross-cutting CGP idea has
a public page a reader can be sent to. Three of its pages are the
[homepage](homepage.md#the-offload-rule-and-the-pages-it-offloads-to)'s offload destinations,
specified [below](#the-three-pages-the-homepage-offloads-to).

- **Where they live**: `docs/concepts/`, recorded in [pages/concepts.md](../pages/concepts.md)
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Raw material**: [cgp/concepts/](../../cgp/concepts/README.md), rewritten rather than copied
- **Reading**: the shared set and [the concept pages' row](README.md#concept-pages) of the reading
  map

## Writing style

Write every page under `docs/concepts/` in **natural-writing**'s natural style: each sentence builds
on the last, paragraphs connect the reasoning, and sentence lengths vary, with lists for sets of
distinct items and prose for an argument. Keep the concept and its purpose the subject of the
opening; an example may introduce it, but the reader must understand that the page explains the idea,
not the example's domain. Preserve technical conditions, exceptions, and uncertainty when revising.

## What an explanation page is not

- **Not a [tutorial](tutorial.md)**, which carries a reader step by step and withholds what they do
  not need yet. An explanation assumes nobody is following along, which frees it to take the long way
  round, discuss alternatives, and admit complications.
- **Not a [reference page](reference.md)**, which specifies a construct completely for a reader
  looking one thing up. An explanation names constructs but never enumerates their syntax.
- **Not the homepage**, which makes the idea click in one screen and a bounded essay. The homepage
  links down to these pages, and they do not re-earn the reader's attention.

## What every explanation page owes its reader

- **Answer "why", not "how do I".** The page organizes around a question a reader would ask aloud
  (*why can't Rust do this?*, *what is actually generated?*, *should I use this?*) and is finished
  when it is answered. If the next sentence would be "now add this to your `Cargo.toml`", the material
  belongs in a tutorial.
- **Explain the existing thing properly before improving on it.** CGP
  [enhances Rust's trait system rather than replacing it](../../communication-strategy/identity.md),
  so a page that opens on coherence as a limitation has the argument backwards. The
  [RustLab transcript](../blog/rustlab-2025-coherence.md) is the model: it establishes that the trait
  system's global lookup gives Rust transitive dependency injection, so coherence is *correct*, before
  a word about working around it.
- **Be as long as the idea needs, and say so at the top**, with a sentence or two on what the page
  covers and how far it goes.
- **Show code as illustration, not as steps.** Snippets make an argument concrete and are read rather
  than typed; they may elide bodies with `/* ... */` and are never numbered as instructions.
- **State the cost**: what the subject costs or where it stops applying, since skeptics and
  evaluators read these pages to the end.
- **End by routing, not by concluding.**

## Where CGP departs from Diátaxis

Diátaxis's account of explanation is adopted: it is understanding-oriented, read away from the work,
may discuss alternatives and history, makes connections, and permits judgement. Two divergences
follow from decisions made elsewhere:

- **Opinion is allowed but not personal.** The site speaks in the project voice, so ground a
  judgement rather than attribute it: "this is more machinery than a plain trait needs", not "I think".
  Where an argument depends on the author's reasons, state them impersonally and link the blog post or
  transcript where he makes them.
- **Mechanism is allowed.** A Rust programmer will not adopt what they cannot see through, so *How CGP
  works* is about mechanism and any page may show generated code where showing it is the argument. The
  line that holds is enumeration: showing what a macro produces is explanation, listing every form it
  accepts is reference.

## Turning a concept document into an explanation page

**A concept document is a rewrite source, not a copy source.** It is written for an agent that has
loaded the `/cgp` skill, so it uses "provider trait", "impl-side dependency", and `IsProviderFor` as
known vocabulary. Three transformations make it public:

- **Apply the vocabulary schedule**: defer or gloss the terms
  [vocabulary.md](../../communication-strategy/vocabulary.md) defers, and define the rest in plain
  language on first use.
- **Add the motivation the document assumes**: what the concept means and why it matters, with the
  concept as the subject of the opening.
- **Remove the internal machinery** (`DelegateComponent`, `IsProviderFor`, the `Symbol<…>` list) unless
  the page's subject *is* that machinery, in which case introduce it as the mechanism behind the model.

The synchronization rule binds the page and its document in both directions. A concept page may cut
a project's scenario down to what the concept needs; its code must still compile, and need not match
the project.

## The page shape

**Open with the concept, its purpose, and the page's scope**, any example supporting that purpose.
The opening paragraph names **Context-Generic Programming** once beside a plain description and links
the Introduction. Where the concept concerns choosing an implementation, as coherence, the
consumer/provider split, and wiring do, it relates a short form of the tag line, as in "CGP extends
Rust with pluggable trait implementations, and Rust's coherence rules are why that needs more than an
ordinary impl"; otherwise, as with the `Send`-bound workaround, it leaves the line out, per the
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page). Every
page carries a written `description` and a problem-oriented `title` in the reader's words, per
[formats.md](../../communication-strategy/formats.md#titles-first-lines-and-search), written in the
same edit as the opening.

**Develop the idea in as many sections as it takes**, under the argument's own headings.

**Close with two fixed sections, in this order.** *What it costs* names what the idea costs or where it
stops applying, and is required. *Where to go next* routes to the neighbouring concept, the tutorial
that puts the idea to work, and the reference pages for its constructs; where a [Projects](project.md)
example page shows the idea in a running program, the list ends with it, labelled *In practice:*, as a
comparison is labelled *Comparison:*, once that page is published.

The written [Consumer and provider traits](https://contextgeneric.dev/docs/concepts/consumer-and-provider-traits)
page is the model.

## The three pages the homepage offloads to

The homepage's three explanation destinations are Concepts pages: *Why CGP exists* is **Bypassing
coherence**, *How CGP works* is **Consumer and provider traits** with **Impl-side dependencies** beside
it, and *When to use CGP* is **Modularity Hierarchy**. Each specification below is that page's.

### Why CGP exists

**Bypassing coherence is the page the homepage links most**, the long form of its first essay section,
organized around *why can't Rust do this already?* It runs in five movements:

1. **The trait system doubles as dependency injection**: a generic impl requires `where T: Display`
   without any caller naming it, and the compiler resolves that bound and every one beneath it.
2. **This works only if every lookup finds the same implementation**, which the overlap and orphan
   rules buy, so coherence is a guarantee rather than a restriction.
3. **What the guarantee costs**: two blanket impls that could both match one type are rejected even
   when the author knows which applies, and a foreign trait cannot be implemented for a foreign type.
4. **The workarounds**, the newtype and the marker-struct-plus-helper-trait pattern developers
   [reinvent independently](../../communication-strategy/evidence.md), named rather than taught.
5. **The move**: the implementation's `Self` becomes a type the implementing crate owns, so both rules
   are satisfied, and coherence is **restored locally**, because each type names one provider. The page
   exists to earn "Coherence is not repealed; it is scoped."

It is built from [coherence](../../cgp/concepts/coherence.md) and
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), with the
[RustLab transcript](../blog/rustlab-2025-coherence.md) as the model for pacing and the
[modular serialization example](../../examples/modular-serialization.md) for verified code, and it
names the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) at the end, because a
reader just told coherence can be escaped needs to hear that most code should not.

**It stays at the basic tier.** The five movements end the page: no parameter-targeted component, no
per-value dispatch, no type standing for an application, and none of the context-shape vocabulary.
Its examples are tier-3 retrofits, a self-targeted trait such as `CanEncode` wired onto the types that
use it (`String`, `Vec<u8>`). How far the idea scales, and the application shape with its transitions
and qualifiers, belong to *Modularity Hierarchy*, taught as the
[comprehension barrier](../../communication-strategy/readers.md) and
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target)
prescribe; this page hands off in a sentence.

### How CGP works

**The page for a reader who believes the pitch and wants to see through the macros**, organized
around *what is actually generated, and what does it cost?*, and the site's answer to
["macros are magic"](../../communication-strategy/message.md#the-objections-readers-bring). It covers,
in order:

- the **two traits** one definition produces, and why the split makes the overlap legal;
- the **wiring table** as a compile-time lookup, described with the settings-map analogy before any
  trait name;
- **what a call resolves to**, traced once end to end;
- the **plain Rust** a small example expands into, ideally from
  [`cargo cgp expand`](../../cgp/reference/cargo-cgp.md) so the reader can reproduce it;
- **why none of it costs anything at runtime**: no vtable, no container, nothing in the binary for an
  unused provider;
- briefly, that **wiring is lazy**, which is why a check exists.

It is built from [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md),
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md), and
[check traits](../../cgp/concepts/check-traits.md). It is the one page in the tier that may name
`DelegateComponent` and `IsProviderFor`, late, as the machinery behind a model that has already landed.

### When to use CGP, and when not

**Modularity Hierarchy is a hybrid**: an explanation walking the five tiers of the hierarchy, a section
each with illustrative code built from the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md)
concept, which stays their source of truth, then a decision-guide tail that is shorter, scannable,
and uses tables. It is where the homepage's cost section hands a skeptic, and the only public page
that draws CGP's boundary.

- **The tail** renders [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp)
  for a public reader: the rule of thumb, the alternative-by-alternative guide with each alternative's
  home ground conceded first, and the cases where CGP is the wrong tool. Never disparage an
  alternative, and if a table is used, every row concedes a case where the other tool wins.
- **The agent-support mitigation belongs here**, one of its two places, beside the learning curve,
  the diagnostics, and the wiring volume, as a smaller cost rather than a disappearing one; it never
  softens a boundary, since a codebase with one application still belongs on `#[cgp_fn]` alone.
- **It decides which of the three shapes to reach for**, as two questions rather than a taxonomy: *is
  the operation about the data, or about the application?* (a value context and the retrofit shape,
  or an environmental context), and *does it concern a type you don't own that different applications
  must treat differently?* (if so, the target moves into a parameter). State that the application
  shape is where most CGP code lives. Since the coherence page stops before the shapes, this page
  introduces the application context, building it from code as the
  [comprehension barrier](../../communication-strategy/readers.md) describes.

## Placing them in the docs tree

The section sits at `docs/concepts/` with a `_category_.json` and `sidebar_position` front matter,
under the mechanics and stock-Docusaurus policy in [site.md](../site.md#how-the-site-is-built). The
category is labelled **Concepts**, never "Explanation", which is the organizers' term and which
Diátaxis itself keeps out of navigation; "Concepts" also matches the knowledge base's name. The
sidebar orders the pages as a reader meets the ideas rather than as the catalog lists them;
[pages/concepts.md](../pages/concepts.md) records the order.

## What must not be on an explanation page

- **No instructions**: no install steps, no `Cargo.toml` edits, no numbered sequence to follow.
- **No exhaustive syntax**: one use of a construct is explanation; its accepted forms belong on its
  [reference page](reference.md).
- **No first-person narration**; link the [transcript](../blog/rustlab-2025-coherence.md) or a blog
  post where the argument wants a person behind it.
- **No unmotivated mechanism**: each piece of machinery answers a question the page has already made
  the reader ask, so `IsProviderFor` is earned on *How CGP works* and not on *Why CGP exists*.
- **No claim without its cost.**

## Checking a draft

- **State the page's organizing question** and check the page answers it, and only it; a second
  question is a second page.
- **Check the frame**: the page explains what Rust already does, correctly and sympathetically, before
  improving on it, the most common way a CGP explanation goes wrong.
- **Read it through in natural style**: each sentence builds on the last, and the opening establishes
  the concept and its purpose, with examples supporting it.
- **Find the cost**, and check the voice: no first person, judgements grounded.
- **Check what leaked in**: install steps, syntax tables, or unearned machinery.
- **Verify every snippet** against the source and the `/cgp` skill, preferring code verified in
  [examples/](../../examples/README.md).
