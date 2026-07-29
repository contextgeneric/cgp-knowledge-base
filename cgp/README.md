# The `cgp` library

This directory documents the CGP language extension itself — the `cgp` crates, their macros, and the
constructs those macros generate. It is one member section of the [CGP knowledge base](../README.md),
and its subject is what CGP *means*: what each construct does, what code it expands into, how the
pieces fit together, and how the macros that produce them are built. The corresponding member project
is [`cgp`](https://github.com/contextgeneric/cgp), and every claim here is verified against that
project's source.

Context-Generic Programming (CGP) is a language extension for Rust, with pluggable trait
implementations at compile-time. In ordinary Rust a trait has one implementation per type; CGP lets
one trait have many interchangeable implementations and lets each context choose which one it uses,
through a small wiring table the compiler resolves statically — so the flexibility costs nothing at
runtime. It is an ordinary library on stable Rust that desugars to plain traits and impls, adopted
one component at a time, and it reaches beyond swappable implementations to abstract types each
context picks for itself, extensible records and variants, and a family of composable handlers.

The `/cgp` skill gives a fast orientation on all of that; this section is the durable record that
goes deeper and stays in sync with the code. Read the two together.

## Why this exists

The base's [README](../README.md#why-this-exists) makes the general case that CGP's meaning has to be
recorded in prose because the macro source does not show it. This section is where that reconstruction
lives for the library: an agent reading
[crates/macros/cgp-macro-core](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core)
sees token-stream manipulation and AST transforms, not the meaning they produce, and the meaning —
"`#[cgp_component]` generates a consumer trait, a provider trait, and two blanket impls that connect
them" — has to be reconstructed by mentally running the macro. Documented once, it is read rather than
re-derived on every visit.

What makes that documentation checkable is a third artifact. A reference document's Expansion section
states the intended generated code in plain language, and the expansion snapshots in
[crates/tests/cgp-macro-tests](https://github.com/contextgeneric/cgp/tree/main/crates/tests/cgp-macro-tests)
pin what the macro really emits, so a reviewer can hold the prose, the code, and the snapshot against
each other and see whether all three agree. Keeping them agreeing is a hard requirement of any change
— see [AGENTS.md](AGENTS.md) for this section's rules and [../AGENTS.md](../AGENTS.md) for the ones the
whole base shares.

## How it is organized

This section is divided into five parts, described below in no particular order. Each answers a
different question about CGP, so a reader picks the one that matches their need rather than reading
them in sequence.

The [reference/](reference/README.md) directory holds one document per CGP construct — one for
`cgp_component`, one for `cgp_impl`, one for `delegate_components`, and so on. Each document is
self-contained and explains a single construct completely: its purpose, its accepted syntax, the
exact code it desugars to, worked examples, and links to the constructs it relates to. The
[reference index](reference/README.md) lists every construct and tracks which ones are documented.

The [concepts/](concepts/README.md) directory holds the cross-cutting conceptual overviews that span
multiple constructs — the consumer/provider duality, dependency injection, namespaces, the handler
family, and so on — each explaining one idea and linking down into the reference documents for the
mechanics. Where the reference explains the individual trees, the concepts explain the shape of the
forest.

The [guides/](guides/README.md) directory holds the guides to *writing* CGP — documents that direct
the choices an author makes, whether between two constructs that could express the same thing or
about the shape of a component before any construct is chosen. Where the reference and concepts
explain what a construct means and why it exists, a guide is prescriptive: it recommends a default
form, names the trade-offs of the alternatives, and usually walks a concrete before/after
refactoring. Deciding what a component is about and how many methods it carries, choosing a
construct's vanilla-looking form over its explicit equivalent, keeping wiring tables short with
namespaces, and debugging a wiring that will not compile all live here.

The [errors/](errors/README.md) directory catalogs the compiler errors CGP produces *after* codegen —
input a macro accepts and lowers to Rust that then fails to compile — organized by the kind of error
rather than by the macro that produced it. Each document records the anatomy of one class: the mistake
that triggers it, the shape of the diagnostic, whether the compiler *surfaces* or *hides* the root
cause, and how [`cargo-cgp`](reference/cargo-cgp.md) reshapes it. That axis and the dividing line
against the failures a macro raises by *rejecting* its input are explained in the
[catalog's README](errors/README.md).

The [implementation/](implementation/README.md) directory documents the *internals* of the macros —
how each one is built, as opposed to what it does for a user: its entry function, the pipeline stages
it drives, the AST types it parses into, the helper functions that synthesize each generated item, its
corner cases and known limitations, and every pointer into the test suite. An agent asked to review,
debug, or extend the macro source reads here first.

## What lives elsewhere

Three parts of CGP's documentation serve the whole ecosystem rather than this section, so they sit at
the base's top level: the worked [examples/](../examples/README.md) these documents quote their
snippets from, the [related-work/](../related-work/README.md) comparisons with the ideas CGP resembles,
and the [communication-strategy/](../communication-strategy/README.md) guidance for writing about CGP
in public. A fourth view lives outside this repository entirely — the `/cgp` skill, in
[`cgp-skills`](https://github.com/contextgeneric/cgp-skills), because a skill is deployed on its own
and may not link back to anything here. All four are bound by the same synchronization rule as this
section, so a construct change propagates into whichever of them shows it.

## How to use it

An agent working on CGP should read the relevant reference document before changing a construct, and
should consult the `/cgp` skill for the conceptual framing that ties constructs together. The
reference documents assume familiarity with the vocabulary the skill establishes — consumer traits,
provider traits, providers, wiring, and so on — and focus on precise per-construct semantics rather
than re-teaching the paradigm. Read the two together: the skill for the shape of the forest, the
reference for the individual trees. When the task is to change the macro rather than to use it, read
the construct's implementation document alongside its reference.
