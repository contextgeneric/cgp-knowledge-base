# Area calculation tutorial series

The site's only sustained teaching material: a four-page series that carries a reader from ordinary
Rust functions, through the coherence wall, to configurable compile-time dispatch with composable
higher-order providers, and finally to catching a wiring mistake at the line that made it — using one
running example the whole way.

- **URL** — <https://contextgeneric.dev/docs/tutorials/area-calculation/>
- **Source** — [docs/tutorials/area-calculation/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/tutorials/area-calculation)
- **Pages** — an unnumbered `index.md` framing the problem, then
  `context-generic-functions.md` (position 1), `static-dispatch.md` (position 2), and
  `checking.md` (position 3)
- **Status** — Current

## What it teaches

The **index** teaches no CGP at all, and that is deliberate. It writes `rectangle_area(width, height)`
as a plain function, then `scaled_rectangle_area(width, height, scale_factor)` which must accept and
forward parameters it does not use, and names the first problem: explicit parameter threading grows
with the call chain. It then tries the conventional fix — group the fields into a `Rectangle` struct
and write methods — and names the second problem: the methods are now coupled to one concrete type, so
adding `color`, `pos_x`, and `pos_y` makes calling `rectangle_area` tedious, and a third party wanting
`pos_z` must ask upstream or fork. The page closes by stating what would fix both, without naming any
construct.

**Context-Generic Functions** delivers that fix. `#[cgp_fn]` with `#[implicit]` arguments makes
`rectangle_area` work on any context with `width` and `height` fields; `#[derive(HasField)]` opts a
struct in; `#[uses(RectangleArea)]` lets `scaled_rectangle_area` call it without knowing its
requirements; and a `print_rectangle_area` function shows the value of `#[cgp_fn]` even with no
implicit arguments at all. Two contexts, `PlainRectangle` and `ScaledRectangle`, coexist with neither
knowing about the other.

A clearly-marked optional **"How it works"** section then shows the desugaring: a `RectangleArea`
trait, a simplified `RectangleFields` getter trait, and a blanket impl connecting them, with the
`#[uses]` bound appearing as `Self: RectangleArea`. It covers borrowed versus owned implicit
arguments, the zero-cost claim, the generalization from a bespoke getter to `HasField`, and a
comparison to **Scala implicit parameters** that distinguishes CGP's name-and-type field resolution
from Scala's scope-based type resolution.

**Static Dispatch** is where the series earns its length. It adds `circle_area`, observes that
`scaled_circle_area` duplicates `scaled_rectangle_area`, and proposes a unified `CanCalculateArea`
trait. Implementing it per context is boilerplate; implementing it with two blanket impls fails, and
the tutorial *shows the compiler error* and explains it with a struct that has `width`, `height`,
**and** `radius`, so the reader sees why Rust cannot choose. `#[cgp_component]` then introduces the
provider trait, `#[cgp_impl]` gives implementations names, and — importantly — the tutorial shows
providers being called *explicitly* as `RectangleAreaCalculator::area(&rectangle)` before any wiring
exists, including calling both providers on the ambiguous struct. Only then does it bind a provider to
a context, first by hand-writing the consumer impl and then by replacing that with
`delegate_components!`, presenting the table as a lookup table with an actual table in the prose.
`#[use_provider]` and higher-order providers close the series, with `ScaledAreaCalculator<Inner>`
generalizing the per-shape scaled calculators, and a note that composed providers are just generic
types that can be aliased.

**Checking and Debugging** closes the series on the question the first three parts leave unasked: what
happens when the wiring is wrong. It mis-wires `PlainCircle` to `RectangleAreaCalculator`, shows that
the program still compiles, and names the reason — wiring is lazy, so an entry is checked when the
component is used rather than when it is written. It then carries that one mistake through three
diagnostics: the raw `E0599` at the call site, which names neither the missing field nor the provider
and points at the line that is correct; the `E0277` that `check_components!` moves to the wiring site,
which names the chain but spells the field name as a `Chars` list; and `cargo cgp check`, which leads
with the missing fields in English. It fixes the wiring, shows the check passing, and closes with an
optional *How it works* section giving the hand-written equivalent of a check — a trait whose
supertrait is the consumer trait, and an impl that asserts it.

The series makes a strong zero-cost argument in its own section: no vtables, no unsafe, no runtime
resolution, all wiring inside Rust's own trait system, and no external compile-time processing.

## The teaching contract

**Objective.** A reader finishes able to define a component, write two named implementations that
would otherwise conflict, wire each context to the one it needs, and compose implementations with a
higher-order provider — and able to say why each step was necessary.

**Prerequisites.** Basic Rust, and "a basic familiarity with Rust traits will be helpful" per the
index. The series does *not* assume knowledge of blanket implementations, coherence, or the orphan
rule; it teaches coherence from scratch when it hits it. It does not assume the reader has done
[Hello World](hello-world.md), though the two overlap.

**Concept sequence.** Plain functions → concrete-context methods → `#[cgp_fn]` + `#[implicit]` →
`#[uses]` → *(optional desugaring)* → a second shape → the need for a unified trait → the coherence
error → `#[cgp_component]` → `#[cgp_impl]` → explicit provider calls → hand-written consumer impls →
`delegate_components!` → `#[use_provider]` → higher-order providers → lazy wiring → the call-site
failure → `check_components!` → `cargo cgp check` → *(optional desugaring)*.

Two orderings in that sequence carry the series and must not be disturbed. **The problem always
precedes the construct**: every step opens with code that is unsatisfactory for a stated reason, and
the construct arrives as the fix. And **the explicit form always precedes the sugar**: providers are
called by name before wiring exists, and the consumer trait is implemented by hand before
`delegate_components!` replaces it, so the reader understands the table as an abbreviation for
something they have already written rather than as magic.

**Level of explanation.** Deeper than [Hello World](hello-world.md) but still gated. Desugaring lives
in explicitly-marked optional sections in part one and is largely absent from part two;
`IsProviderFor`, `DelegateComponent`, and the generated blanket impls are never named, though the
lookup they perform is described. The series says a table is built and consulted at compile time, and
stops there.

**Vocabulary.** It uses "consumer trait," "provider trait," "provider," "named implementation," and
"component name," each introduced at the moment it becomes necessary — and never earlier. That
matches the introduction order in
[vocabulary.md](../../communication-strategy/vocabulary.md).

**Part four extends the contract in one way, deliberately.** `CanUseComponent` and `IsProviderFor`
appear there, where the first three parts never name them, because the diagnostics the page quotes
name them and a page about reading errors cannot hide the words the errors use. They arrive last, in
the optional desugaring section, framed as machinery that exists so a failure can explain itself
rather than as anything a reader writes. `DelegateComponent` is still never named.

## How it relates to the knowledge base

The constructs are [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md),
[`#[implicit]`](../../cgp/reference/attributes/implicit.md),
[`#[uses]`](../../cgp/reference/attributes/uses.md),
[`#[derive(HasField)]`](../../cgp/reference/derives/derive_has_field.md),
[`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md),
[`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md),
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md), and
[`#[use_provider]`](../../cgp/reference/attributes/use_provider.md). The concepts, in the order the
series meets them, are [implicit arguments](../../cgp/concepts/implicit-arguments.md),
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md),
[coherence](../../cgp/concepts/coherence.md),
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), and
[higher-order providers](../../cgp/concepts/higher-order-providers.md).

**The [area calculation example](../../examples/area-calculation.md) is this series' verified
counterpart** and follows the same progression; it is the source to draw code from when revising, and
the two must be kept in step. The Scala comparison rests on
[implicit-parameters](../../related-work/implicit-parameters.md).

The series is also the site's best execution of the tutorial playbook in
[formats.md](../../communication-strategy/formats.md): it opens on a concrete pain, carries one
running example throughout, leads with vanilla-looking idioms, and defers machinery. Its target reader
is the working developer in [readers.md](../../communication-strategy/readers.md).

## Where it diverges from CGP v0.8.0

The code is current — the series was written for v0.7.0 and nothing it uses changed in v0.8.0 — and
one gap is worth knowing. The two that used to sit here, that checking was never mentioned and that
`cargo-cgp` was never mentioned, are closed by part four.

- **`#[cgp_impl]` appears in both forms.** Part two first shows
  `impl<Context> AreaCalculator for Context where Self: RectangleArea` and then simplifies to
  `impl AreaCalculator`. That is pedagogically deliberate, but only the second form is idiomatic per
  [writing-providers](../../cgp/guides/writing-providers.md), and a reader who stops reading early
  will copy the first.

## Maintaining it

Preserve the two orderings above — problem before construct, explicit before sugar — over anything
else; they are what makes the series work, and they are what an unwary addition breaks.

**The series is sequential, and part four depends on that.** Its code blocks are fragments of the
program part three ends with, and the line numbers in its quoted errors refer to that file — which the
page says in its opening rather than leaving a reader to discover. The
[tutorial guide](../writing-guides/tutorial.md) asks tutorials to stand alone; this series does not,
and part four inherits the property rather than introducing it. The index describes all three parts
and part three now routes forward to part four instead of closing the series.

**Part four's diagnostics are quoted output, not remembered output**, and a revision that changes its
program must re-run all three rather than editing the text: `cargo check` at the call site,
`cargo check` with the assertion in place, and `cargo cgp check`. Its program and the mis-wired fixture are
both in the website repository's `example-code` crate, at `tests/tutorials/` and
`tests/compile_fail/tutorials/`, so the checked error the page quotes is pinned by a blessed
`.stderr`. Note that rustc abbreviates the `Chars` list differently depending on how it is invoked, so
the page's quote matches the pinned fixture rather than any one local run.

A **fifth part on namespaces**, drawn from the
[social media app example](../../examples/social-media-app.md), is the natural step after it — but
namespaces only pay off once a wiring table is long, and this series' table has one entry, so it needs
a bigger running example rather than a bolt-on section.
