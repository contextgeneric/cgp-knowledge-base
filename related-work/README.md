# CGP Related Work

This directory compares CGP to the outside ideas it resembles, one document per external concept,
framework, or language feature that solves a problem CGP also solves, or that a reader might already know
well enough to learn CGP through. Each document explains the related work faithfully and in depth, weighs
what its users like and dislike about it, and then positions CGP against it. The documents exist to make
CGP legible to readers who arrive with an existing mental model, by meeting that model on its own terms
before showing where CGP diverges.

## Why this exists

Related-work documents serve *future user-facing documentation*, not the reader trying to learn CGP
directly. When an agent later writes a tutorial, an article, or a landing page aimed at people who
already know dependency injection or implicit parameters, it reads the matching document here first,
then builds the CGP explanation on the intuitions those readers already hold. The eventual audience is a
practitioner of the related concept. The audience of the document itself is the agent preparing to
address them, and its job is to supply the honest comparison and the positioning strategy that writing
will rest on.

Honesty is the whole value of the section. A document that flatters CGP or misrepresents the related
work is worse than useless, because the readers it ultimately serves are the people most able to see
through both. So each document explains the related work well enough that its own community would
recognize the account, states the pros and cons of both sides, and names the cases where the related
work is the better tool. The [AGENTS.md](AGENTS.md) in this directory carries the authoring rules,
chiefly the obligations every document must meet and the rule that sets this section apart from the
rest of the knowledge base: unlike examples, related-work documents cite their sources and compile their
foreign-language snippets.

## How related work differs from the other sections

Related work answers a question none of the other sections do: *how does CGP relate to the idea I
already know?* A [reference document](../cgp/reference/README.md) explains one CGP construct completely.
A [concept document](../cgp/concepts/README.md) explains one cross-cutting CGP idea. An
[example](../examples/README.md) develops one use case end to end. A [guide](../cgp/guides/README.md)
directs a choice between CGP constructs. All four look inward at CGP. A related-work document looks
outward. It takes something from outside CGP as the subject, explains it on its own terms, and uses CGP
only as the point of comparison. Where an example is re-derived as native material with no pointer to
its origin, a related-work document is the opposite: its credibility depends on being a traceable, cited
account of the external thing.

The documents therefore lean on the rest of the base rather than restating it. A related-work document
links to the [concepts](../cgp/concepts/README.md) for the CGP idea a comparison rests on and to the
[reference](../cgp/reference/README.md) for the exact syntax of any construct it shows, keeping its own
focus on the external concept and the comparison. When a CGP snippet is needed, it is drawn from the
running scenarios the [examples](../examples/README.md) already use, so the CGP side of every comparison
speaks the knowledge base's shared vocabulary. Every document also says which
[context shape](../cgp/concepts/modularity-hierarchy.md) its CGP snippets wire, since the comparisons
span all three.

## The catalog

Each document below names an external concept and compares it to CGP. The authoring rules for adding one
live in [AGENTS.md](AGENTS.md). The first two documents are the ones a Rust reader compares CGP to before
any other, so they are listed first; the rest are grouped by the tradition they come from.

- [Rust's own proposals](rust-language-proposals.md) — specialization (RFC 1210, unstable since 2016
  with a lifetime soundness hole), the dictionary-passing account of traits, Boxy's named and incoherent
  impls, Tyler Mandry's contexts and capabilities, and Cairo as the Rust-like language that shipped
  named impls. CGP is read as a library-level desugaring of a fragment of each, with providers as named
  impls, implicit arguments as capabilities, and the context as the root dictionary, and with two stated
  limits: no inference from scope and no nested bindings.
- [C++ policy-based design, CRTP, and concepts](policy-based-design.md) — Alexandrescu's policies and
  host classes, the curiously recurring template pattern, and C++20 concepts. CGP is the same
  compile-time composition with the policy interface declared as a trait, the provider body checked at
  definition rather than at instantiation, and the choices gathered into one wired context rather than
  a parameter list.
- [Capabilities](capabilities.md) — the five things the word names: object capabilities (E, Pony, seL4,
  WASI, `cap-std`), capability-based security in operating systems and hardware, Pony's reference
  capabilities and Linux privilege bits (which share only the word), effects as capabilities (Effekt,
  Scala's `CanThrow` and capture checking), and the Rust community's implicit-value, sandboxing, and
  ownership-token senses. CGP is capability-like in the effects sense (a provider declares what it
  requires and the context supplies it, checked at compile time) and is not a capability system in the
  object-capability sense: it does not remove ambient authority, its requirements are not unforgeable
  tokens, and its provisioning is fixed per context type.
- [Dependency injection](dependency-injection.md) — the IoC-container and constructor-injection model of
  Spring, Guice, Dagger, and their kin, and how CGP's impl-side dependencies and per-context wiring inject
  dependencies without a container, reflection, or runtime graph.
- [Implicit parameters](implicit-parameters.md) — the implicitly passed context arguments of Scala's
  `given`/`using` and Haskell's `ImplicitParams`, the type-class resolution both build on, and how CGP's
  implicit arguments and context-threaded wiring achieve the same context propagation while trading
  global coherence for per-context choice.
- [Type classes](type-classes.md) — the principled ad-hoc polymorphism of Haskell, Agda, and Lean,
  dictionary passing and coherence, the overlapping and incoherent-instance extensions that strain
  against it, the diamond problem in dependently typed settings, and Dreyer, Harper, and Chakravarty's
  "modular type classes". CGP is a type-class system that removes global coherence and replaces implicit
  resolution with explicit per-context selection, which makes overlapping and incoherent instances
  ordinary and deterministic rather than exceptional and dangerous.
- [ML modules and modular implicits](ml-modules.md) — the signatures, structures, and functors of OCaml
  and Standard ML, and the modular-implicits extension that adds type-directed resolution over them. CGP
  maps components to signatures, providers to structures, and higher-order providers to functors, and
  replaces manual, ordered functor application with a declarative `delegate_components!` table resolved
  per context.
- [Algebraic effects and handlers](algebraic-effects.md) — the operations-and-handlers model of Koka,
  OCaml, Flix, and Eff, where a handler interprets an effect by capturing the continuation and resuming
  it zero, one, or many times. CGP reproduces the effect/handler split only for the exactly-once
  fragment the literature identifies as dynamic binding, resolved statically per context rather than
  dynamically down a call stack, and extended to configuring abstract types.
- [Row polymorphism, structural typing, and extensible data types](row-polymorphism.md) — the
  field-and-variant-shape typing of PureScript's rows and OCaml's polymorphic variants, framed by Morris
  and McKinna's "rows by any other name" row-theory account. CGP brings the same extensible records and
  variants to nominal Rust through derived type-level shapes and trait predicates rather than a built-in
  row kind.
- [Dynamic dispatch, dynamic typing, and prototypal inheritance](dynamic-dispatch.md) — late binding and
  message passing, the vtables and method dictionaries that implement them, duck typing, and
  prototype-based delegation in Self, JavaScript, and Lua. CGP reproduces their openness (many
  implementations behind one interface, behavior shared by delegation with `self` staying bound, defaults
  inherited from a namespace) while resolving all of it statically, so its vtable is a type-level table
  erased before runtime.
- [Reflection and compile-time introspection](reflection.md) — Bevy's runtime reflection, Zig's
  `comptime` as the compile-time model, and Rust's nightly reflection MVP read from its source, set
  against Go, Java, C++26, D, and facet. CGP reaches the same generic-over-structure payoff by encoding a
  type's shape as type-level lists the trait system resolves against, shown through `cgp-serde`'s
  `SerializeFields`, carrying field types as types so it recurses into them, checked when written, and
  extended to behavior and abstract-type selection.
