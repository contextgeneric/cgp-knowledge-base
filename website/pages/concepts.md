# Concepts

Concepts is the site's explanation tier: one page per cross-cutting CGP idea, answering *why does
CGP work this way* rather than *how do I write it*.

- **URL:** <https://contextgeneric.dev/docs/concepts/>
- **Source:** [docs/concepts/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/concepts)
- **Status:** Current: the index and all eighteen pages are written
- **How it was made:** written by an agent from [cgp/concepts/](../../cgp/concepts/README.md); level
  one of the four in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What it covers

The section is a top-level category at `docs/concepts/`, position 5, with a hand-written index as its
category link. It has eighteen pages, one per document under
[cgp/concepts/](../../cgp/concepts/README.md) with matching file names, so the mapping is one to one.
Three shared diagrams live in `static/img/`: *Bypassing coherence* carries coherence scoped to each
provider, and *Consumer and provider traits* the split and the wiring table, so the ideas the
homepage offloads to reuse one drawing.

**Every page's code has a compiled counterpart** in the
[`example-code` crate](../site.md#the-example-code-crate), one file per page; eighteen pages show
code and the index none. Every quoted error is real compiler output, including the `E0119` and
`E0117` on *Bypassing coherence*, the `E0599` / `CanUseComponent` / `[CGP-E001]` progression on
*Checking your wiring*, and the two override conflicts on *Namespaces*.

**The sidebar order is the order a reader meets the ideas:** the coherence problem and the trait
split, then the three faces of dependency injection, then composition and scale, then the applied
ideas, with *Recovering `Send` bounds* and *Modularity Hierarchy* last.

**Every page and the index are in natural-writing style.** The index groups reading links by the
question they answer. Each page opens with the idea and its purpose, and the openings distinguish
shared type choices, reusable wiring, explicit checks, computation composition, structural data
operations, and stronger async bounds before their scenarios. Running examples enter in the body,
each tied to the requirement or limit it shows, with short comparisons (type selection against type
imports, matching against building) and consequences that form one argument in connected prose. Cost
sections relate each limit to the mechanism it qualifies; tables and reading lists stay where readers
compare or choose.

### What each page must preserve

The pages carry qualifications that a shortening revision is likely to drop:

- **Bypassing coherence:** the tier's opening argument, following the guide's five-movement outline
  at the basic tier. It develops transitive trait resolution before overlap and orphan checks, then
  shows complete provider bodies and explicit calls encoding one `String` as text and hexadecimal
  before introducing wiring. That wiring makes one program-wide choice per value type, and
  component-key ownership still stops a downstream crate from wiring a foreign component onto a
  foreign value type. The section *Selecting one provider for each type* keeps the original wiring
  anchor. Independent application choices are deferred to *Modularity Hierarchy*.
- **Consumer and provider traits:** context-style `Self` inside `#[cgp_impl]` against Rust's ordinary
  provider-side `Self`, with the exception for a provider's own associated types and constants;
  multi-item components; a call trace explaining why `App` first fills both the context and
  delegating-provider roles; simplified providers that keep the rejected blanket implementations'
  context bounds; `send_welcome` as a generic caller bounded only by the consumer trait; that direct
  and wired implementations of one consumer trait cannot coexist for a context; and the hand-written
  expansion including the `IsProviderFor` supertrait, which only the introductory trait pair omits.
- **Abstract types:** shared type selection against provider compatibility, and when a type
  dependency must appear in the interface.
- **Aggregate providers:** bundles checked against actual contexts; namespace customization needs
  unbound paths.
- **Checking your wiring:** ordinary trait assertions, component checks, and diagnostic rewriting kept
  distinct; one broken context followed unchecked, checked, and checked through the toolchain; its
  quoted output is abbreviated.
- **Implicit arguments:** matching `HasField` implementations; cloning against borrowing, named
  getters, and wireable field selection.
- **Modular error handling:** reusable failure reporting against context-selected error
  representation; configurable construction and wrapping against propagation through `Result` and
  `?`; a `#[cgp_fn(CanParsePort)]` blanket trait through a string context with per-source dispatch
  and a domain-error enum whose `From` conversions keep the parse error; `CanParseConfigPort` showing
  wrapping and transitive dependencies without wrapper wiring; formatting losing source structure;
  and an application-specific raiser for unrelated domain failures. Keep the conversion requirements
  and the separate raising and wrapping checks when changing types or backends.
- **Namespaces:** inherited routes against bound destinations; inherited components need explicit
  checks. Joining a namespace generates a forwarding impl for every key it answers, so a direct entry
  for a bound key overlaps it with `E0119`, the
  [override-conflict](../../cgp/errors/wiring/namespace-override-conflict.md) class; only an unbound
  path is open to a context, which is why the page teaches namespace design as *what varies?*.
- **Modularity Hierarchy:** a hybrid of five tier sections with illustrative code and a
  decision-guide tail that leads with a rule of thumb and uses tables, each alternatives row conceding
  a case where the other tool wins. Every tier obeys coherence, one context can still justify
  providers, and generic context instantiations stay distinct types. It is the site's only public
  home for [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp)'s boundary
  material, which the reference's *When to use it* sections point at.
- **Monadic handlers:** the direct-composition mismatch limited to `Computer`; the outer error
  propagation fallible handlers already supply; the continuation cases for a nested result
  transformer.
- **Type-level DSLs:** `#[cgp_impl]` for the addition provider, in the page and its counterpart; trait
  resolution selects operations without evaluating function bodies.
- **Recovering Send bounds:** an absent signature guarantee rather than a removed auto-trait
  implementation; the response bound repeated at generic use sites; `Send` distinct from executor
  lifetime and output requirements.
- **Dispatching:** handler selection and coverage checked statically while variant tests and calls
  run at runtime; dependencies between record-building steps; the wrapper recursive matchers need.
- **Extensible records:** generic assembly beside ordinary constructors; every source field must match
  a target field; the strict builder against optional-field extensions.
- **Extensible variants:** handlers reused across closed enums; structural casts need matching
  payload types; the single-payload derive restriction.
- **Handlers:** the interfaces compared in a table; promotion's error and borrowing requirements;
  sequential pipelines; the separate need for `Send` futures.
- **Higher-order providers:** static provider selection against runtime computation; aliases do not
  verify a composition's requirements; `UseContext` traced from a collection trait to its element
  trait; the switch from shape contexts to an application context marked; an inner request must not
  route back to the same wrapper.
- **Impl-side dependencies:** stable generic caller bounds against what concrete contexts satisfy;
  ordinary functions and blanket implementations first, then email providers and a greeting with
  implicit field access; `CanGreet` does not imply `HasName`; the shared error stays in the public
  interface while `CanRunJob` remains a dependency of the generated `RunJobs`; `run_batch` requires
  only `RunJobs` and names its result through the implied `HasErrorType`; one error choice per context
  against a generic function's per-call choice; runtime and storage requirements may stay on a
  provider whose signatures do not expose their types. The traits/values/types and type-choice
  sections keep their original anchors.

### Conventions the pages settle

- **The `cargo cgp check` concession is the canonical sentence, with no version:** the tool leads
  with the root cause for the classes it recognizes and does not yet reshape every class, per
  [vocabulary.md](../../communication-strategy/vocabulary.md), linking the
  [classes that pass through](https://contextgeneric.dev/docs/cargo-cgp/reading-output#errors-that-pass-through-unchanged)
  where it says more.
- **A page that crosses between context shapes marks the crossing where it happens,** in prose beside
  the code.
- **The encoding example is shared with the front page:** the hero's rejected `CanEncode` pair over
  `Display` and `AsRef<[u8]>` is the code *Bypassing coherence* opens on, and the `EncodeAsText`
  provider name carries across, so a reader meets one running example.

## The page shape

A concept page is an argument rather than a specification. It names the question it answers and
where it ends; shows what ordinary Rust already does, working, before what it cannot share; develops
the idea with illustrative code; and closes with **What it costs**, which is required, and **Where to
go next**, which routes. *Modularity Hierarchy* adds its decision-guide tail before the two closing
sections. The rules are in [writing-guides/explanation.md](../writing-guides/explanation.md).

## How it relates to the knowledge base

Each page derives from the internal document of the same name under
[cgp/concepts/](../../cgp/concepts/README.md), which stays the source of truth. The
[guides](../../cgp/guides/README.md) reach the site through a page's *What it costs* and *Where to go
next*, and implementation documents are dropped.

Each page records which of CGP's three context shapes its code is in, since no signature marks it:

- **Consumer and provider traits:** **environmental, self-targeted** throughout, the `App`/`TestApp`
  email swap from [message.md](../../communication-strategy/message.md#the-problems-cgp-removes), one
  of the first places a reader meets a type that stands for an application, described without the
  qualifiers. It draws on [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md),
  [coherence](../../cgp/concepts/coherence.md), and the
  [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md).
- **Bypassing coherence:** a **value context, self-targeted** retrofit, `CanEncode` wired onto
  `String` and `Vec<u8>`, never crossing into the other shapes, which it defers to *Modularity
  Hierarchy*, per the [*Why CGP exists* spec](../writing-guides/explanation.md#why-cgp-exists).
- **Modularity Hierarchy:** all three shapes across tiers 3 and 4, from the
  [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) concept, with the boundary from
  [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp).

## Maintaining it

- Write and revise every page in natural-writing style, as the
  [explanation guide](../writing-guides/explanation.md#writing-style) requires, keeping the concept as
  the subject. Keep the compiled examples, quoted diagnostics, heading anchors, and reference links.
- The pages and their internal documents are bound by the
  [synchronization rule](../../AGENTS.md#the-synchronization-rule) in both directions; a page that
  disagrees with its document is the defect.
- **Do not turn a concept page into a reference page:** naming a construct and showing one use is
  explanation, listing its forms is reference.
- **Do not drop the cost section;** the least credulous readers come for it, and a trim targets it
  first.
