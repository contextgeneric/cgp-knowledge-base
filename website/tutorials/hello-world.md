# Hello World tutorial

The site's first-contact tutorial: a single page that gets a reader from an empty project to a working
context-generic function in a few minutes, teaching only one construct and one derive before the
payoff.

- **URL**: <https://contextgeneric.dev/docs/tutorials/hello>
- **Source**: [docs/tutorials/hello.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/tutorials/hello.md)
- **Pages**: one, at `sidebar_position: 2` in the tutorials category
- **Status**: Current; the version pin is stale on `main` and updated on the `v0.8.0` branch

## What it teaches

The tutorial adds the `cgp` crate and imports the prelude, defines a `greet` function with `#[cgp_fn]`
taking `&self` and one `#[implicit] name: &str` argument, and defines a `Person` struct with
`#[derive(HasField)]` so `person.greet()` works with no wiring, trait impl, or configuration. A second
struct, `PersonWithAge`, then makes the point the tutorial exists for: `greet` works unchanged on both,
because it depends on a *field* rather than a type.

An explicitly optional **"Behind the Scenes"** section shows the plain-Rust equivalent (a `HasName`
getter trait, a `Greet` trait with a blanket impl over any `T: HasName`, and a hand-written
`HasName for Person`), then makes three points: the macros are sugar over ordinary trait machinery with
no hidden compile-time or runtime logic; an implicit argument is a plain field read, so zero cost; and
the real machinery uses the general `HasField` trait rather than a per-trait getter, which lets a
function and a struct in unrelated crates fit together in a third.

## The teaching contract

**Objective.** A running program and one durable idea: a CGP function depends on the fields a context
has rather than its type, so one function serves many structs. Components, providers, and wiring are
not goals.

**Prerequisites.** Basic Rust and adding a dependency. It assumes no CGP knowledge and no comfort with
blanket implementations or generics: the optional section that uses them links an external explanation
of blanket impls. It does not assume the reader has read the Introduction.

**Register and shape.** First-principles, on a **value context** whose component targets `Self`:
`Person` is the thing being greeted.

**Concept sequence.** Prelude, `#[cgp_fn]`, `#[implicit]`, `#[derive(HasField)]`, a second context, then
the optional desugaring. The reader sees a working program before any explanation of why it works, the
progressive disclosure [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers)
prescribes. **The second context is the payoff and stays in that position**: earlier removes the
motivation, later loses the reader.

**Level of explanation.** Shallow in the body and moderate in the appendix. The body never mentions
consumer traits, provider traits, `Symbol!`, or `PhantomData`. The appendix shows a *simplified*
desugaring, a bespoke `HasName` trait rather than `HasField`, and says it is a simplification and why.
That two-level split is the tutorial's main craft; pushing real desugaring into the body breaks the
contract.

**Vocabulary.** "Context-generic method", "implicit argument", and "zero cost"; "wiring" once in
passing; "component" and "provider" only in the closing paragraph, as the next tutorials' subject,
consistent with [vocabulary.md](../../communication-strategy/vocabulary.md).

## How it relates to the knowledge base

The constructs are [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md) with
[`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments and
[`#[derive(HasField)]`](../../cgp/reference/derives/derive_has_field.md) over
[`HasField`](../../cgp/reference/traits/has_field.md); the idea is
[implicit arguments](../../cgp/concepts/implicit-arguments.md), and the appendix's blanket impl is
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md). The tutorial follows
[reading-context-fields](../../cgp/guides/reading-context-fields.md): an implicit argument, not a
getter trait, reads a context's own field.

Its reader is the first-contact skimmer in [readers.md](../../communication-strategy/readers.md), and
its "no hidden logic, no unsafe, no runtime cost" claims are the zero-cost strength in
[message.md](../../communication-strategy/message.md#the-strengths-worth-advertising). The nearest
verified code is the opening of the [area calculation example](../../examples/area-calculation.md).

## Where it diverges from CGP v0.8.0

**Only the version pin, and only on `main`**: the published page pins `cgp = "0.7.0"` while its code is
written against [v0.8.0](../../releases/v0-8-0.md). The `v0.8.0` branch pins `cgp = "0.8.0"`, which
resolves once the release is published, so the page and the release land together. `#[cgp_fn]`,
`#[implicit]`, and `#[derive(HasField)]` are unchanged, and the appendix remains an accurate
simplification.

**One caveat**: the appendix's `HasName` returns `&str` from a `String` field, as `#[cgp_auto_getter]`
supports, but presents it as hand-written code. Before adding any claim about how values are fetched,
check the access rules in [`#[implicit]`](../../cgp/reference/attributes/implicit.md): an owned
argument is read by reference and cloned, a `&str` is read from a `String` field through
`AsRef::as_ref`, and a plain `&T` is borrowed with no conversion.

## Maintaining it

**Update the version pin, and resist additions.** The tutorial's value is that it is short enough to
finish; anything larger belongs in the [area calculation series](area-calculation.md), which the
closing paragraph points to, promising components and providers "in the next tutorials". Preserve the
second context, which is the payoff, and the two-level split between the body and the appendix.
