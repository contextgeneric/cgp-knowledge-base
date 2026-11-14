# Comparisons

Comparisons places CGP among related ideas for a reader who arrives knowing one: one page per
related-work document, plus an index that routes by background.

- **URL:** <https://contextgeneric.dev/docs/comparisons/>
- **Source:** [docs/comparisons/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/comparisons)
- **Status:** Current: the index and all eleven pages are written, each with its `example-code`
  mirror, and revised against the naming rule and the
  [comparison guide](../writing-guides/related-work.md)
- **How it was made:** ported by an agent from [related-work/](../../related-work/README.md); level
  one of the four in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md). The author's
  read of each page's two judging sections, per the
  [authorship rule](../../communication-strategy/ai-disclosure.md#the-two-claims-that-are-easiest-to-get-wrong),
  is outstanding.

## What it covers

The section is a top-level category at `docs/comparisons/`, labelled *Comparisons*, at position 6.
Every page follows the shape [writing-guides/related-work.md](../writing-guides/related-work.md)
specifies: an orientation paragraph that names Context-Generic Programming, links the Introduction,
and relates a short form of the tag line; an *In your terms* table that glosses "context" on first
use; a compressed refresher of the compared idea; the CGP side beside it; what each approach costs,
with the canonical `cargo cgp check` sentence; where the other tool is the better choice; what to
expect that differs; onward routing; Sources, opening with the toolchain sentence; and the comparison
variant of the provenance note.

The sidebar follows the internal catalog's order: *Rust's own proposals* and *Policy-based design*,
then *Type classes*, *ML modules*, *Implicit parameters*, *Algebraic effects*, and *Row
polymorphism*, then *Dependency injection*, *Dynamic dispatch*, *Reflection*, and *Capabilities*.

Fourteen concept pages end *Where to go next* with one entry per relevant comparison, labelled
*Comparison:*; *Dispatching*, *Monadic handlers*, *Type-level DSLs*, and *Recovering `Send` bounds*
carry none.

### What each page must preserve

Every page explains its analogy point first, with explicit limits:

- **Algebraic effects:** dependency checking against effect typing; normal return against a
  termination guarantee.
- **Capabilities:** fixed wiring against runtime authority; confinement stays with the value type and
  the enforcement environment.
- **Dependency injection:** provider selection against object construction and lifecycle management.
- **Dynamic dispatch:** dynamic typing against runtime polymorphism; coexistence with trait objects.
  Its namespace example uses the [namespaces concept](../../cgp/concepts/namespaces.md)'s compiled
  open-slot shape rather than the internal document's `@cgp.core.error => @app` redirect.
- **Implicit parameters:** Scala's scoped givens, Haskell's named implicit parameters, and global
  type-class instances kept apart; CGP keeps Rust's coherence checks.
- **ML modules:** associated-type selection against sealing; scoped selection in modular implicits;
  the Functoria analogy limited to provider assembly; `ScaledArea` needs an explicit inner provider,
  because `new` adds no `UseContext` default.
- **Policy-based design:** nondependent checks at definition against dependent checks at
  instantiation; concepts and policy aliases acknowledged; const generics and runtime polymorphism
  stay available beside CGP; the greeting uses `this->` for dependent-base lookup. The three C++
  examples were compiled and run with GCC 15.2.0 in C++23 mode.
- **Reflection:** role correspondences rather than language-feature equivalence.
- **Row polymorphism:** predicate-based rows against a row kind and against row inference.
- **Rust's own proposals:** proposal syntax against runnable Rust; what CGP cannot infer or nest.
- **Type classes:** scoped coherence against global uniqueness; where a canonical instance is the
  simpler choice.

The overview distinguishes compiled examples from documentation-checked and proposal examples. The
context shape is stated in prose beside the code on every page: the encoder pair wires
environmental, parameter-targeted contexts (`ApiServer`, `Firmware`, `AppA`, `AppB`); the greeter
and error examples environmental, self-targeted ones; the area, rectangle, person, and cast examples
value contexts.

## How it relates to the knowledge base

Each page derives from the internal document of the same name under
[related-work/](../../related-work/README.md), which stays the source of truth and names the page
it feeds under its Sources heading. The port applied the guide's four transformations: the internal
*Presenting CGP to someone who knows this* sections became the *In your terms* tables and the *What
to expect that differs* sections; the refreshers were compressed; every internal link was repointed
to a Concepts, reference, tutorial, or blog page; and Sources were kept. The two documents that drew
on the [unpublished incoherent-Rust draft](../blog/incoherent-rust-today.md) state those points as
the project's analysis or attribute them to the [RustLab transcript](../blog/rustlab-2025-coherence.md),
never citing the draft: the Rust proposals page states the Cairo reading, the context-as-dictionary
framing, and the single-context limits as the project's analysis, and attributes to the transcript
what the transcript makes; the algebraic-effects page keeps the coeffects pointer as a pointer. Both
pages gain a citation when the incoherent-Rust post publishes.

**The pages' CGP code differs from the internal documents' in two places,** so a later
synchronization should not "fix" it:

- **The encoder pair replaces `cgp-serde`'s providers.** Where the type-classes,
  implicit-parameters, and Rust-proposals documents show `UseSerde` and `SerializeBytes` on
  `cgp-serde`'s `ValueSerializer`, the pages show `EncodeWithDisplay`, `EncodeBytes`, and
  `EncodeAsHex` on the `CanEncode<Value>` component from
  [message.md](../../communication-strategy/message.md#the-problems-cgp-removes), which compiles
  without `serde`.
- **The reflection page's example is a local field writer,** `WriteFields` over a `FieldsWriter`
  recursion producing a JSON-like string, modeled on `cgp-serde`'s `SerializeRecordFields` and
  linking it. The published `cgp-serde` and its `main` depend on `cgp` 0.7.0, so the verification
  crate cannot use it beside `cgp` 0.8.0.

The foreign-language snippets come from the internal documents, whose Sources sections record their
verification toolchains; a prose revision does not imply a snippet was recompiled.

## Where it diverges

Nothing is stale, and two things decay on their own:

- The reflection page describes Rust's nightly `type_info` API, marked unstable; a revision re-reads
  [tracking issue #146922](https://github.com/rust-lang/rust/issues/146922) and the project goal.
- Every page pins the toolchains that compiled its foreign snippets (GHC 9.10, Scala 3.8.4, OCaml
  5.5.0, Koka 3.2.3, Flix 0.76.0, Zig 0.16, PureScript 0.15.15, Agda 2.8.0, Lean 4.34.0, GCC 15.2.0,
  `cap-std` 3), which the internal documents own.

## Maintaining it

- The pages are bound to their internal documents, and to the compared tools, by the
  [synchronization rule](../../AGENTS.md#the-synchronization-rule): a change to how Scala resolves a
  `given` updates the document and the page together.
- The CGP code has a mirror in `example-code/tests/comparisons/`, one file per page, with the RFC 1210
  specialization snippet as a compile-fail fixture confirming it is rejected on stable.
- **Do not reintroduce positioning prose;** a sentence telling the reader which intuitions to build on
  belongs to the internal document.
- **Do not soften or fold away the section where the other tool wins.**
- **Do not let a sentence about another community's tool read as mockery;** attribute the opinion
  with its citation or cut it.
