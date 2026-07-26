# Area calculation tutorial series

The site's only sustained teaching material: a three-page series that carries a reader from ordinary
Rust functions, through the coherence wall, to configurable compile-time dispatch with composable
higher-order providers — using one running example the whole way.

- **URL** — <https://contextgeneric.dev/docs/tutorials/area-calculation/>
- **Source** — [docs/tutorials/area-calculation/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/tutorials/area-calculation)
- **Pages** — an unnumbered `index.md` framing the problem, then
  `context-generic-functions.md` (position 1) and `static-dispatch.md` (position 2)
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
`delegate_components!` → `#[use_provider]` → higher-order providers.

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

The code is current — the series was written for v0.7.0 and nothing it uses changed in v0.8.0 — but
three gaps are worth knowing.

- **`#[cgp_impl]` appears in both forms.** Part two first shows
  `impl<Context> AreaCalculator for Context where Self: RectangleArea` and then simplifies to
  `impl AreaCalculator`. That is pedagogically deliberate, but only the second form is idiomatic per
  [writing-providers](../../cgp/guides/writing-providers.md), and a reader who stops reading early
  will copy the first.
- **Checking is never mentioned.** No page calls
  [`check_components!`](../../cgp/reference/macros/check_components.md) or explains that wiring is
  lazy, so a reader who mis-wires a context meets the failure at the call site with no idea that a
  compile-time assertion exists. Given that [check traits](../../cgp/concepts/check-traits.md) are
  how CGP errors are made readable, this is the series' largest gap.
- **`cargo-cgp` is never mentioned.** The series makes strong claims about compile-time safety without
  telling the reader what a wiring failure looks like or that
  [`cargo cgp check`](../../cargo-cgp/reference/usage.md) exists to make it readable — which
  [formats.md](../../communication-strategy/formats.md) explicitly asks a tutorial to do, setting the
  error-message expectation honestly *before* the reader hits one.

## Maintaining it

Preserve the two orderings above — problem before construct, explicit before sugar — over anything
else; they are what makes the series work, and they are what an unwary addition breaks.

The clear next step is a **third part on checking and debugging**, covering lazy wiring,
`check_components!`, and `cargo cgp check`, written from
[check traits](../../cgp/concepts/check-traits.md), the
[debugging guide](../../cgp/guides/debugging.md), and
[cargo-cgp/reference/usage.md](../../cargo-cgp/reference/usage.md). That would close the largest gap
without disturbing the existing ramp. A fourth part on namespaces, drawn from the
[social media app example](../../examples/social-media-app.md), is the natural step after it — but
namespaces only pay off once a wiring table is long, and this series' table has one entry, so it needs
a bigger running example rather than a bolt-on section.
