# Hello World tutorial

The site's first-contact tutorial: a single page that gets a reader from an empty project to a working
context-generic function in a few minutes, deliberately teaching only one construct and one derive
before showing the payoff.

- **URL** — <https://contextgeneric.dev/docs/tutorials/hello>
- **Source** — [docs/tutorials/hello.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/tutorials/hello.md)
- **Pages** — one, sitting at `sidebar_position: 2` in the tutorials category
- **Status** — Current, with one stale version pin

## What it teaches

The tutorial moves in four steps. It adds the `cgp` crate and imports the prelude. It defines a
`greet` function with `#[cgp_fn]`, taking `&self` and one `#[implicit] name: &str` argument, and
explains each of the three annotations in a sentence. It defines a `Person` struct with
`#[derive(HasField)]` and calls `person.greet()` — with no wiring, no trait impl, and no
configuration. Then it introduces a second struct, `PersonWithAge`, to make the point the whole
tutorial exists for: `greet` works unchanged on both, because it depends on a *field* rather than on a
type.

A closing **"Behind the Scenes"** section, explicitly optional, shows the plain-Rust equivalent — a
`HasName` getter trait, a `Greet` trait with a blanket impl over any `T: HasName`, and a hand-written
`HasName for Person` — and then makes three points on top of it: that CGP macros are syntactic sugar
over ordinary trait machinery with no hidden compile-time or runtime logic; that implicit-argument
access is a plain field read and therefore zero cost; and that the real machinery uses the general
`HasField` trait rather than a generated per-capability getter, which is what lets a function and a
struct in unrelated crates fit together in a third.

## The teaching contract

**Objective.** A reader finishes with a running program and one durable idea: that a CGP function
depends on the fields a context has rather than on the context's type, so the same function serves
many structs. Nothing else is a goal — not components, not providers, not wiring.

**Prerequisites.** Basic Rust and the ability to add a dependency. The tutorial assumes *no* CGP
knowledge and, notably, does not assume comfort with blanket implementations or generics: the optional
section that uses them links out to an external explanation of blanket impls rather than presuming
one. It does not assume the reader has read the Introduction page.

**Concept sequence.** Prelude, then `#[cgp_fn]`, then `#[implicit]`, then `#[derive(HasField)]`, then
a second context — and only then, optionally, the desugaring. The ordering principle is that the
reader sees a *working program* before any explanation of why it works, which is the progressive
disclosure that [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers)
prescribes. The second context is the payoff and must stay in that position; moving it earlier removes
the motivation, moving it later loses the reader.

**Level of explanation.** Deliberately shallow in the body and moderate in the appendix. The body
never mentions consumer traits, provider traits, `Symbol!`, or `PhantomData`. The appendix shows a
*simplified* desugaring — a bespoke `HasName` trait rather than `HasField` — and then says explicitly
that it is a simplification and why. That two-level structure is the tutorial's main craft, and a
revision that collapses it by pushing real desugaring into the body would break the contract.

**Vocabulary.** The tutorial says "context-generic method," "implicit argument," and "zero cost," and
avoids "component," "provider," and "wiring" entirely — consistent with the deferral list in
[vocabulary.md](../../communication-strategy/vocabulary.md).

## How it relates to the knowledge base

The two constructs are [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md) with
[`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments and
[`#[derive(HasField)]`](../../cgp/reference/derives/derive_has_field.md) over the
[`HasField`](../../cgp/reference/traits/has_field.md) trait; the idea behind them is
[implicit arguments](../../cgp/concepts/implicit-arguments.md), and the blanket-impl mechanism the
appendix reveals is [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md). The
guidance that an implicit argument, not a getter trait, is the default for reading a context's own
field is [reading-context-fields](../../cgp/guides/reading-context-fields.md) — which this tutorial
follows correctly.

For framing, the reader it targets is the first-contact skimmer in
[readers.md](../../communication-strategy/readers.md), and the "no hidden logic, no
unsafe, no runtime cost" claims are the zero-cost selling point in
[message.md](../../communication-strategy/message.md#the-capabilities-worth-advertising), backed by the survey evidence in
[evidence.md](../../communication-strategy/evidence.md) that the Rust
community explicitly prizes runtime performance.

The nearest verified code is the [area calculation example](../../examples/area-calculation.md),
whose opening steps cover the same constructs.

## Where it diverges from CGP v0.8.0

Only one thing, and it is trivial to fix: the `Cargo.toml` snippet pins `cgp = "0.7.0"` while the
current release is 0.8.0. Everything else on the page is current — `#[cgp_fn]`, `#[implicit]`, and
`#[derive(HasField)]` are unchanged, and the simplified desugaring in the appendix remains an accurate
simplification.

One caveat rather than a divergence: the appendix's `HasName` trait returns `&str` from a `String`
field, which the real `#[cgp_auto_getter]` supports but which is presented here as hand-written code.
That is fine as a simplification, but a reviser adding detail should check the actual access rules in
[`#[implicit]`](../../cgp/reference/attributes/implicit.md) — in particular that an *owned* implicit
argument now requires `Copy` rather than `Clone` — before making any claim about how values are
fetched.

## Maintaining it

Update the version pin. Beyond that, resist additions. The tutorial's value is that it is short enough
to finish, and every construct added to it costs a reader who would otherwise have reached the end.
Anything larger belongs in the [area calculation series](area-calculation.md), which is where the page
should continue to point — as its closing paragraph already does, promising components and providers
"in the next tutorials."

Two specific things to preserve: the second context, which is the entire payoff, and the two-level
split between the body and the optional appendix.
